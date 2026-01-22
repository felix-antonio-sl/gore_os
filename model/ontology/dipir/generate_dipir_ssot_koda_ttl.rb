#!/usr/bin/env ruby
# frozen_string_literal: true

require "optparse"
require "set"
require "yaml"

DEFAULT_INPUT = "/Users/felixsanhueza/Developer/gorenuble/staging/procesos_dipir/dipir_ssot_koda.yaml"
DEFAULT_OUTPUT = "model/ontology/dipir/dipir_ssot_koda.ttl"

def turtle_escape(value)
  value
    .to_s
    .gsub("\\", "\\\\")
    .gsub("\"", "\\\"")
    .gsub("\t", "\\t")
    .gsub("\r", "\\r")
    .gsub("\n", "\\n")
end

def xsd_string(value)
  %("#{turtle_escape(value)}"^^xsd:string)
end

def xsd_boolean(value)
  value ? "true" : "false"
end

def xsd_integer(value)
  %("#{Integer(value)}"^^xsd:integer)
end

def safe_local_name(value)
  # macOS system Ruby 2.6 may lack unicode_normalize stdlib; we only need a
  # conservative transliteration for Spanish identifiers used in DIPIR SSOT.
  transliteration = {
    "á" => "a", "à" => "a", "ä" => "a", "â" => "a", "ã" => "a", "Á" => "A", "À" => "A", "Ä" => "A", "Â" => "A", "Ã" => "A",
    "é" => "e", "è" => "e", "ë" => "e", "ê" => "e", "É" => "E", "È" => "E", "Ë" => "E", "Ê" => "E",
    "í" => "i", "ì" => "i", "ï" => "i", "î" => "i", "Í" => "I", "Ì" => "I", "Ï" => "I", "Î" => "I",
    "ó" => "o", "ò" => "o", "ö" => "o", "ô" => "o", "õ" => "o", "Ó" => "O", "Ò" => "O", "Ö" => "O", "Ô" => "O", "Õ" => "O",
    "ú" => "u", "ù" => "u", "ü" => "u", "û" => "u", "Ú" => "U", "Ù" => "U", "Ü" => "U", "Û" => "U",
    "ñ" => "n", "Ñ" => "N",
    "ç" => "c", "Ç" => "C",
  }

  text = value.to_s.chars.map { |ch| transliteration.fetch(ch, ch) }.join
  text = text.gsub(/[^A-Za-z0-9_]/, "_")
  text = text.gsub(/_+/, "_").gsub(/\A_+|_+\z/, "")
  text = "X" if text.empty?
  text
end

class TurtleWriter
  def initialize
    @lines = []
  end

  def line(text = "")
    @lines << text
  end

  def block(subject, predicates_and_objects)
    predicates_and_objects = predicates_and_objects.reject { |_, obj| obj.nil? }
    line(subject)
    predicates_and_objects.each_with_index do |(predicate, object), index|
      terminator = index == predicates_and_objects.size - 1 ? "." : ";"
      line("\t#{predicate} #{object} #{terminator}")
    end
    line
  end

  def to_s
    @lines.join("\n")
  end
end

options = { input: DEFAULT_INPUT, output: DEFAULT_OUTPUT }

OptionParser.new do |parser|
  parser.banner = "Usage: #{File.basename($PROGRAM_NAME)} [--input PATH] [--output PATH]"
  parser.on("--input PATH", "KODA SSOT YAML input (default: #{DEFAULT_INPUT})") { |v| options[:input] = v }
  parser.on("--output PATH", "Turtle output path (default: #{DEFAULT_OUTPUT})") { |v| options[:output] = v }
end.parse!

ssot = YAML.load_file(options[:input])

actors_master = ssot.dig("process_definition", "core", "actors_master") || []
templates = ssot.dig("process_definition", "core", "templates") || {}
variants = ssot.dig("process_definition", "variants") || {}
orchestration = ssot["orchestration"] || {}

styles = Set.new
node_types = Set.new
connection_types = Set.new(%w[sequence message_throw message_catch])
resolution_types = Set.new
budget_subtitles = Set.new
process_states = Set.new
tramitation_types = Set.new
boundary_boxes = Set.new

actors_master.each do |actor|
  styles << actor["style"] if actor["style"]
end

templates.each_value do |tmpl|
  styles << tmpl["style"] if tmpl.is_a?(Hash) && tmpl["style"]
  tramitation_types << tmpl["tramitation"] if tmpl.is_a?(Hash) && tmpl["tramitation"]
  (tmpl["steps"] || []).each do |step|
    styles << step["style"] if step["style"]
    node_types << step["type"] if step["type"]
    tramitation_types << step["tramitation"] if step["tramitation"]
  end
end

variants.each do |variant_key, variant|
  characteristics = variant["characteristics"] || {}
  resolution_types << characteristics["resolution_type"] if characteristics["resolution_type"]

  if variant_key.start_with?("subt_")
    parts = variant_key.split("_").drop(1)
    parts.each do |p|
      next unless p.match?(/\A\d+\z/)
      budget_subtitles << p
    end
  end

  (variant["flow_sequence"] || []).each do |section|
    boundary_boxes << section["boundary_box"] if section["boundary_box"]
    process_states << section["state_name"] if section["state_name"]
    (section["steps"] || []).each do |step|
      styles << step["style"] if step["style"]
      node_types << step["type"] if step["type"]
      tramitation_types << step["tramitation"] if step["tramitation"]
    end
  end

  (variant["connections"] || []).each do |conn|
    connection_types << conn["type"] if conn["type"]
  end
end

# Pre-index nodes for resolving next_step references.
variant_node_by_id = {}
variant_node_by_step_code = {}
global_nodes_by_id = Hash.new { |hash, key| hash[key] = [] }

variants.each do |variant_key, variant|
  by_id = {}
  by_step = {}

  (variant["flow_sequence"] || []).each do |section|
    (section["steps"] || []).each do |step|
      step_id = step["id"]
      next unless step_id

      node_subject = "dipird:FlowNode_#{safe_local_name(variant_key)}_#{safe_local_name(step_id)}"
      by_id[step_id.to_s] = node_subject
      by_step[step["step"].to_s] = node_subject if step["step"]
      global_nodes_by_id[step_id.to_s] << node_subject
    end
  end

  variant_node_by_id[variant_key] = by_id
  variant_node_by_step_code[variant_key] = by_step
end

tw = TurtleWriter.new

tw.line("@prefix dipir: <urn:gorenuble:ontology:dipir:> .")
tw.line("@prefix dipird: <urn:gorenuble:data:dipir:> .")
tw.line("@prefix gist: <https://w3id.org/semanticarts/ns/ontology/gist/> .")
tw.line("@prefix owl: <http://www.w3.org/2002/07/owl#> .")
tw.line("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
tw.line("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
tw.line("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .")
tw.line("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
tw.line

tw.block(
  "<urn:gorenuble:data:dipir:dipir_ssot_koda>",
  [
    ["a", "owl:Ontology"],
    ["owl:imports", "<urn:gorenuble:ontology:dipir>"],
    ["skos:prefLabel", xsd_string("DIPIR SSOT KODA — dataset RDF")],
    ["skos:definition", xsd_string("Dataset generado desde #{options[:input]} para representar el SSOT DIPIR (GORE Ñuble) usando la extensión dipir sobre gist 14.")],
  ],
)

unresolved_nodes = {}

# Reference data: Visualization styles
styles.sort.each do |style|
  tw.block(
    "dipird:VisualizationStyle_#{safe_local_name(style)}",
    [
      ["a", "dipir:VisualizationStyle"],
      ["skos:prefLabel", xsd_string(style)],
    ],
  )
end

# Reference data: Node types
node_types.sort.each do |node_type|
  tw.block(
    "dipird:FlowNodeType_#{safe_local_name(node_type)}",
    [
      ["a", "dipir:FlowNodeType"],
      ["skos:prefLabel", xsd_string(node_type)],
    ],
  )
end

# Reference data: Connection types
connection_types.sort.each do |conn_type|
  tw.block(
    "dipird:FlowConnectionType_#{safe_local_name(conn_type)}",
    [
      ["a", "dipir:FlowConnectionType"],
      ["skos:prefLabel", xsd_string(conn_type)],
    ],
  )
end

# Reference data: Resolution types
resolution_types.sort.each do |res_type|
  tw.block(
    "dipird:ResolutionType_#{safe_local_name(res_type)}",
    [
      ["a", "dipir:ResolutionType"],
      ["skos:prefLabel", xsd_string(res_type)],
    ],
  )
end

# Reference data: Budget subtitles
budget_subtitles.sort.each do |subtitle|
  tw.block(
    "dipird:BudgetSubtitle_#{safe_local_name(subtitle)}",
    [
      ["a", "dipir:BudgetSubtitle"],
      ["skos:prefLabel", xsd_string(subtitle)],
      ["skos:notation", xsd_string(subtitle)],
    ],
  )
end

# Reference data: Process states
process_states.sort.each do |state|
  tw.block(
    "dipird:ProcessState_#{safe_local_name(state)}",
    [
      ["a", "dipir:ProcessState"],
      ["skos:prefLabel", xsd_string(state)],
    ],
  )
end

# Reference data: Tramitation types
tramitation_types.sort.each do |tramitation|
  tw.block(
    "dipird:TramitationType_#{safe_local_name(tramitation)}",
    [
      ["a", "dipir:TramitationType"],
      ["skos:prefLabel", xsd_string(tramitation)],
    ],
  )
end

# Reference data: Boundary boxes
boundary_boxes.sort.each do |box|
  tw.block(
    "dipird:BoundaryBox_#{safe_local_name(box)}",
    [
      ["a", "dipir:BoundaryBox"],
      ["skos:prefLabel", xsd_string(box)],
    ],
  )
end

# Actor roles
actors_master.each do |actor|
  actor_id = actor["id"]
  next unless actor_id

  tw.block(
    "dipird:ActorRole_#{safe_local_name(actor_id)}",
    [
      ["a", "dipir:ActorRole"],
      ["skos:prefLabel", xsd_string(actor["name"] || actor_id)],
      ["skos:definition", actor["full_name"] ? xsd_string(actor["full_name"]) : nil],
      ["skos:notation", xsd_string(actor_id)],
      ["dipir:emoji", actor["emoji"] ? xsd_string(actor["emoji"]) : nil],
      ["dipir:isInternal", actor.key?("internal") ? xsd_boolean(actor["internal"]) : nil],
      ["dipir:hasVisualizationStyle", actor["style"] ? "dipird:VisualizationStyle_#{safe_local_name(actor["style"])}" : nil],
    ],
  )
end

# Core process templates (fragments)
templates.each do |template_key, tmpl|
  next unless tmpl.is_a?(Hash)

  tmpl_id = tmpl["id"] || template_key
  tmpl_subject = "dipird:ProcessFragment_#{safe_local_name(template_key)}"

  tw.block(
    tmpl_subject,
    [
      ["a", "dipir:ProcessFragment"],
      ["skos:prefLabel", xsd_string(tmpl["title"] || template_key)],
      ["skos:definition", tmpl["description"] ? xsd_string(tmpl["description"]) : nil],
      ["skos:notation", xsd_string(tmpl_id)],
      ["dipir:hasTramitationType", tmpl["tramitation"] ? "dipird:TramitationType_#{safe_local_name(tmpl["tramitation"])}" : nil],
      ["dipir:isLoop", tmpl.key?("is_loop") ? xsd_boolean(tmpl["is_loop"]) : nil],
    ],
  )

  # Template steps (if present)
  (tmpl["steps"] || []).each do |step|
    step_id = step["id"]
    next unless step_id

    node_subject = "dipird:FlowNodeTemplate_#{safe_local_name(template_key)}_#{safe_local_name(step_id)}"

    tw.block(
      node_subject,
      [
        ["a", "dipir:FlowNodeTemplate"],
        ["gist:isPartOf", tmpl_subject],
        ["skos:prefLabel", xsd_string(step["action"] || step_id)],
        ["skos:notation", xsd_string(step_id)],
        ["dipir:stepCode", step["step"] ? xsd_string(step["step"]) : nil],
        ["dipir:hasActorRole", step["actor"] ? "dipird:ActorRole_#{safe_local_name(step["actor"])}" : nil],
        ["dipir:hasNodeType", step["type"] ? "dipird:FlowNodeType_#{safe_local_name(step["type"])}" : nil],
        ["dipir:hasVisualizationStyle", step["style"] ? "dipird:VisualizationStyle_#{safe_local_name(step["style"])}" : nil],
        ["dipir:hasTramitationType", step["tramitation"] ? "dipird:TramitationType_#{safe_local_name(step["tramitation"])}" : nil],
      ],
    )
  end
end

# Process variants (full flows)
variants.each do |variant_key, variant|
  variant_subject = "dipird:ProcessVariant_#{safe_local_name(variant_key)}"
  meta = variant["metadata"] || {}
  characteristics = variant["characteristics"] || {}

  statements = [
    ["a", "dipir:ProcessVariant"],
    ["skos:prefLabel", xsd_string(meta["name"] || variant_key)],
    ["dipir:variantKey", xsd_string(variant_key)],
    ["dipir:sourceFile", meta["original_file"] ? xsd_string(meta["original_file"]) : nil],
    ["dipir:hasResolutionType", characteristics["resolution_type"] ? "dipird:ResolutionType_#{safe_local_name(characteristics["resolution_type"])}" : nil],
    ["dipir:requiresCgr", characteristics.key?("cgr_required") ? xsd_boolean(characteristics["cgr_required"]) : nil],
    ["dipir:requiresDipres", characteristics.key?("dipres_required") ? xsd_boolean(characteristics["dipres_required"]) : nil],
    ["dipir:hasPagare", characteristics.key?("has_pagare") ? xsd_boolean(characteristics["has_pagare"]) : nil],
  ]

  if variant_key.start_with?("subt_")
    parts = variant_key.split("_").drop(1).select { |p| p.match?(/\A\d+\z/) }
    parts.each do |subtitle|
      statements << ["dipir:hasBudgetSubtitle", "dipird:BudgetSubtitle_#{safe_local_name(subtitle)}"]
    end
  end

  (variant["actors_active"] || []).each do |actor_id|
    statements << ["dipir:hasActorRole", "dipird:ActorRole_#{safe_local_name(actor_id)}"]
  end

  (variant["uses_templates"] || []).each do |template_key|
    statements << ["gist:isBasedOn", "dipird:ProcessFragment_#{safe_local_name(template_key)}"]
  end

  tw.block(variant_subject, statements)

  # Sections & steps
  ordered_step_nodes = []
  by_id = variant_node_by_id.fetch(variant_key, {})
  by_step_code = variant_node_by_step_code.fetch(variant_key, {})

  (variant["flow_sequence"] || []).each_with_index do |section, section_index|
    section_code = section["section"] || (section_index + 1).to_s
    section_subject = "dipird:FlowSection_#{safe_local_name(variant_key)}_#{safe_local_name(section_code)}"

    tw.block(
      section_subject,
      [
        ["a", "dipir:FlowSection"],
        ["gist:isPartOf", variant_subject],
        ["skos:prefLabel", xsd_string(section["title"] || section_code)],
        ["skos:notation", xsd_string(section_code)],
        ["dipir:hasProcessState", section["state_name"] ? "dipird:ProcessState_#{safe_local_name(section["state_name"])}" : nil],
        ["dipir:hasBoundaryBox", section["boundary_box"] ? "dipird:BoundaryBox_#{safe_local_name(section["boundary_box"])}" : nil],
      ],
    )

    (section["steps"] || []).each do |step|
      step_id = step["id"]
      next unless step_id

      node_subject = "dipird:FlowNode_#{safe_local_name(variant_key)}_#{safe_local_name(step_id)}"

      ordered_step_nodes << { step: step, subject: node_subject }

      tw.block(
        node_subject,
        [
          ["a", "dipir:FlowNodeTemplate"],
          ["gist:isPartOf", section_subject],
          ["skos:prefLabel", xsd_string(step["action"] || step_id)],
          ["skos:notation", xsd_string(step_id)],
          ["dipir:stepCode", step["step"] ? xsd_string(step["step"]) : nil],
          ["dipir:hasActorRole", step["actor"] ? "dipird:ActorRole_#{safe_local_name(step["actor"])}" : nil],
          ["dipir:hasNodeType", step["type"] ? "dipird:FlowNodeType_#{safe_local_name(step["type"])}" : nil],
          ["dipir:hasVisualizationStyle", step["style"] ? "dipird:VisualizationStyle_#{safe_local_name(step["style"])}" : nil],
          ["dipir:hasTramitationType", step["tramitation"] ? "dipird:TramitationType_#{safe_local_name(step["tramitation"])}" : nil],
          ["dipir:cascadePosition", step["cascade_position"] ? xsd_integer(step["cascade_position"]) : nil],
          ["dipir:isFinalApproval", step.key?("is_final_approval") ? xsd_boolean(step["is_final_approval"]) : nil],
          ["dipir:isTermination", step.key?("termination") ? xsd_boolean(step["termination"]) : nil],
          ["dipir:isExternalActor", step.key?("external_actor") ? xsd_boolean(step["external_actor"]) : nil],
          ["dipir:eventType", step["event_type"] ? xsd_string(step["event_type"]) : nil],
          ["dipir:isLoop", step.key?("is_loop") ? xsd_boolean(step["is_loop"]) : nil],
          ["dipir:notes", step["notes"] ? xsd_string(step["notes"]) : nil],
          ["gist:description", step["description"] ? xsd_string(step["description"]) : nil],
        ],
      )
    end
  end

  # Connections inferred from step order + gateway outcomes
  connection_index = 0

  ordered_step_nodes.each_with_index do |item, idx|
    step = item[:step]
    from_subject = item[:subject]

    # Gateways with explicit outcomes
    if step["outcomes"]
      step["outcomes"].each do |outcome|
        next_step_ref = outcome["next_step"]
        ref_key = next_step_ref.to_s
        to_subject = by_id[ref_key] || by_step_code[ref_key]

        if !to_subject
          candidates = global_nodes_by_id[ref_key]
          to_subject = candidates[0] if candidates.size == 1
        end

        unless to_subject
          fallback = "dipird:UnresolvedNodeRef_#{safe_local_name(variant_key)}_#{safe_local_name(next_step_ref)}"
          warn("WARN: unresolved next_step '#{next_step_ref}' in #{variant_key} step #{step["id"]} (#{step["step"]}); using #{fallback}")
          to_subject = fallback
          unresolved_nodes[fallback] ||= { ref: next_step_ref, variant: variant_key }
        end

        connection_index += 1
        conn_subject = "dipird:FlowConnection_#{safe_local_name(variant_key)}_#{format('%03d', connection_index)}"
        tw.block(
          conn_subject,
          [
            ["a", "dipir:FlowConnection"],
            ["gist:isPartOf", variant_subject],
            ["dipir:fromNode", from_subject],
            ["dipir:toNode", to_subject],
            ["dipir:hasConnectionType", "dipird:FlowConnectionType_sequence"],
            ["dipir:conditionText", outcome["condition"] ? xsd_string(outcome["condition"]) : nil],
          ],
        )
      end
      next
    end

    # Terminal nodes do not generate an inferred next edge
    next if step["termination"] == true
    next if step["type"] == "END_EVENT"

    next_item = ordered_step_nodes[idx + 1]
    next unless next_item

    connection_index += 1
    conn_subject = "dipird:FlowConnection_#{safe_local_name(variant_key)}_#{format('%03d', connection_index)}"
    tw.block(
      conn_subject,
      [
        ["a", "dipir:FlowConnection"],
        ["gist:isPartOf", variant_subject],
        ["dipir:fromNode", from_subject],
        ["dipir:toNode", next_item[:subject]],
        ["dipir:hasConnectionType", "dipird:FlowConnectionType_sequence"],
      ],
    )
  end
end

# Orchestration entry gateway routing to variants
orch_meta = orchestration["metadata"] || {}
entry_gateway = orchestration["entry_gateway"] || {}

orch_subject = "dipird:Orchestration_DIPIR"
tw.block(
  orch_subject,
  [
    ["a", "dipir:OrchestrationModel"],
    ["skos:prefLabel", xsd_string(orch_meta["name"] || "Orquestador Procesos DIPIR")],
    ["skos:definition", orch_meta["description"] ? xsd_string(orch_meta["description"]) : nil],
  ],
)

gateway_id = entry_gateway["id"] || "ENTRY_GATEWAY"
gateway_subject = "dipird:FlowNode_orchestration_#{safe_local_name(gateway_id)}"
tw.block(
  gateway_subject,
  [
    ["a", "dipir:FlowNodeTemplate"],
    ["gist:isPartOf", orch_subject],
    ["skos:prefLabel", xsd_string(entry_gateway["action"] || gateway_id)],
    ["skos:notation", xsd_string(gateway_id)],
    ["dipir:hasActorRole", entry_gateway["actor"] ? "dipird:ActorRole_#{safe_local_name(entry_gateway["actor"])}" : nil],
    ["dipir:hasNodeType", "dipird:FlowNodeType_EXCLUSIVE_GATEWAY"],
    ["dipir:hasVisualizationStyle", "dipird:VisualizationStyle_gateway"],
    ["gist:description", entry_gateway["description"] ? xsd_string(entry_gateway["description"]) : nil],
  ],
)

orch_conn_index = 0

def emit_orchestration_outcome(tw:, from_gateway:, orch_subject:, outcome:, parent_condition: nil)
  condition = [parent_condition, outcome["condition"]].compact.join(" / ")
  process_ref = outcome["process_ref"]
  return unless process_ref

  # process_ref: "#process_definition.variants.subt_24" -> "subt_24"
  variant_key = process_ref.split(".").last
  to_subject = "dipird:ProcessVariant_#{safe_local_name(variant_key)}"

  yield(condition, to_subject)
end

outcomes = entry_gateway["outcomes"] || []
outcomes.each do |outcome|
  if outcome["sub_gateway"]
    parent = outcome["condition"]
    (outcome["sub_outcomes"] || []).each do |sub_outcome|
      emit_orchestration_outcome(
        tw: tw,
        from_gateway: gateway_subject,
        orch_subject: orch_subject,
        outcome: sub_outcome,
        parent_condition: parent,
      ) do |condition, to_subject|
        orch_conn_index += 1
        conn_subject = "dipird:FlowConnection_orchestration_#{format('%03d', orch_conn_index)}"
        tw.block(
          conn_subject,
          [
            ["a", "dipir:FlowConnection"],
            ["gist:isPartOf", orch_subject],
            ["dipir:fromNode", gateway_subject],
            ["dipir:toNode", to_subject],
            ["dipir:hasConnectionType", "dipird:FlowConnectionType_sequence"],
            ["dipir:conditionText", condition.empty? ? nil : xsd_string(condition)],
          ],
        )
      end
    end
  else
    emit_orchestration_outcome(
      tw: tw,
      from_gateway: gateway_subject,
      orch_subject: orch_subject,
      outcome: outcome,
    ) do |condition, to_subject|
      orch_conn_index += 1
      conn_subject = "dipird:FlowConnection_orchestration_#{format('%03d', orch_conn_index)}"
      tw.block(
        conn_subject,
        [
          ["a", "dipir:FlowConnection"],
          ["gist:isPartOf", orch_subject],
          ["dipir:fromNode", gateway_subject],
          ["dipir:toNode", to_subject],
          ["dipir:hasConnectionType", "dipird:FlowConnectionType_sequence"],
          ["dipir:conditionText", condition.empty? ? nil : xsd_string(condition)],
        ],
      )
    end
  end
end

unless unresolved_nodes.empty?
  tw.line("# Unresolved node references (next_step targets not defined as nodes in SSOT)")
  tw.line

  unresolved_nodes.sort.each do |subject, info|
    tw.block(
      subject,
      [
        ["a", "dipir:FlowNodeTemplate"],
        ["skos:prefLabel", xsd_string(info[:ref])],
        ["skos:definition", xsd_string("Referencia no resuelta (next_step) en variante #{info[:variant]}.")],
      ],
    )
  end
end

File.write(options[:output], tw.to_s)
puts "Wrote #{options[:output]}"

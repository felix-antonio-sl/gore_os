import {
  GoreBadge,
  Icons,
  RutInput,
  CurrencyInput,
  StatusStepper,
  FirmaDigitalButton,
  IPRCard,
  ProcessTimeline,
  ExpedienteHeader,
  FuncionarioCard,
  ProveedorCard,
  DocumentItem,
} from "@gore-os/ui";
import { useState } from "react";

export function UiShowcase() {
  const [rut, setRut] = useState("");
  const [monto, setMonto] = useState(0);

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="mx-auto max-w-5xl space-y-12">
        {/* Header Section */}
        <section className="space-y-4">
          <h1 className="text-4xl font-bold text-gore-brand">
            GORE OS <span className="text-gore-secondary">UI Kit 4.0</span>
          </h1>
          <p className="text-gray-600">
            Showcase de componentes sociotécnicos alineados a capabilities.
          </p>
        </section>

        {/* Tokens & Atoms */}
        <section className="space-y-4 rounded-lg bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold border-b pb-2">1. Átomos (Tokens)</h2>
          <div className="flex gap-4">
            <GoreBadge>Default (Brand)</GoreBadge>
            <GoreBadge variant="secondary">Secondary</GoreBadge>
            <GoreBadge variant="success">Success (TDE)</GoreBadge>
            <GoreBadge variant="destructive">Destructive (Error)</GoreBadge>
            <GoreBadge variant="outline">Outline</GoreBadge>
          </div>
          <div className="flex gap-4 items-center">
            <Icons.Home size={24} />
            <Icons.FileText size={24} />
            <Icons.CheckCircle size={24} />
            <Icons.AlertTriangle size={24} />
          </div>
        </section>

        {/* Molecules */}
        <section className="space-y-6 rounded-lg bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold border-b pb-2">2. Moléculas (Inputs)</h2>
          <div className="grid grid-cols-2 gap-8">
            <RutInput
              label="RUT Beneficiario"
              onRutChange={(r, v) => setRut(r)}
            />
            <CurrencyInput
              label="Monto Solicitado"
              onValueChange={(v) => setMonto(v)}
            />
          </div>
          <div className="p-4 bg-gray-100 rounded text-sm font-mono">
            RUT: {rut} | Monto: {monto}
          </div>
          
          <div className="space-y-2">
            <h3 className="font-medium text-sm">Stepper de Proceso</h3>
            <StatusStepper
              steps={[
                { id: "1", label: "Ingreso", status: "completed" },
                { id: "2", label: "Revisión TDE", status: "current" },
                { id: "3", label: "Aprobación", status: "pending" },
              ]}
            />
          </div>

          <div className="space-y-2">
            <h3 className="font-medium text-sm">Firma Digital</h3>
             <FirmaDigitalButton
                signerName="Felix Sanhueza"
                onSign={async () => new Promise(resolve => setTimeout(resolve, 2000))}
             />
          </div>
        </section>

        {/* Organisms */}
        <section className="space-y-8 rounded-lg bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold border-b pb-2">3. Organismos (Dominio)</h2>
          
          <div className="space-y-4">
            <h3 className="font-medium">IPR Card (Inversión)</h3>
            <div className="grid grid-cols-2 gap-4">
                <IPRCard
                code="40052312-0"
                name="Reposición Escuela Básica Ñuble"
                amount={4500000000}
                stage="Ejecución"
                status="active"
                location="Chillán"
                />
                 <IPRCard
                code="40051111-K"
                name="Construcción APR San Nicolás"
                amount={120000000}
                stage="RS (Recomendado)"
                status="finished"
                location="San Nicolás"
                />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-medium">Expediente Header & Timeline</h3>
            <div className="border rounded-lg overflow-hidden">
                <ExpedienteHeader
                    type="Expediente Administrativo"
                    id="EXP-2025-00123"
                    title="Solicitud de Transferencia Municipalidad"
                    status="En Trámite"
                    metadata={[
                        { label: "Fecha Ingreso", value: "22/12/2025" },
                        { label: "Responsable", value: "D-FIN / Analista 1" },
                        { label: "Prioridad", value: "Alta" },
                        { label: "Plazo Legal", value: "10 Días" },
                    ]}
                />
                <div className="p-6 bg-gray-50">
                    <ProcessTimeline
                        events={[
                            { id: "1", date: "22/12/2025 09:00", title: "Ingreso Oficina de Partes", actor: "Sistema", type: "info" },
                            { id: "2", date: "22/12/2025 10:30", title: "Validación Documental TDE", actor: "Agent Digitrans", type: "success", description: "Todos los documentos cumplen Norma Técnica." },
                            { id: "3", date: "22/12/2025 12:00", title: "Asignación a Analista", actor: "Jefe Departamento", type: "info" },
                        ]}
                    />
                </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-medium">Entidades Institucionales (GORE / TDE)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FuncionarioCard 
                    nombres="Félix Antonio"
                    apellidos="Sanhueza"
                    email="fsanhueza@gorenuble.cl"
                    cargo="Jefe División"
                    division="D-TDE"
                    estamento="DIRECTIVO"
                    estado="Activo"
                />
                <FuncionarioCard 
                    nombres="María José"
                    apellidos="Pérez"
                    email="mjperez@gorenuble.cl"
                    cargo="Analista Financiero"
                    division="D-FIN"
                    estamento="PROFESIONAL"
                    estado="Activo"
                />
                 <ProveedorCard 
                    rut="76123456-7"
                    razonSocial="Constructora Ñuble Limitada"
                    giro="Obras de ingeniería civil"
                    estadoMercadoPublico="Hábil"
                />
                 <ProveedorCard 
                    rut="12345678-9"
                    razonSocial="Servicios IT SpA"
                    giro="Desarrollo de Software"
                    estadoMercadoPublico="Inhábil"
                />
            </div>
            <div className="mt-4 border p-4 rounded-lg bg-white">
                <h4 className="text-sm font-medium mb-2 text-gray-500">Documentos Recientes</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <DocumentItem 
                        tipo="Resolución Exenta"
                        numero="1456"
                        fecha="20/12/2025"
                        materia="Aprueba bases de licitación proyecto reposición escuela"
                        estado="Tramitada"
                    />
                    <DocumentItem 
                        tipo="Ordinario"
                        numero="550"
                        fecha="21/12/2025"
                        materia="Solicita informe de factibilidad técnica"
                        estado="Enviado"
                    />
                     <DocumentItem 
                        tipo="Factura Electrónica"
                        numero="998877"
                        fecha="18/12/2025"
                        materia="Pago estado de avance N° 1"
                        estado="Pagada"
                    />
                </div>
            </div>
          </div>

        </section>
      </div>
    </div>
  );
}

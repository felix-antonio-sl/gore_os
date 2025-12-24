import { useState, useMemo } from 'react';

// Entity type definition (would come from API in real app)
interface EntityDef {
  id: string;
  name: string;
  domain: string;
  category: string;
  attributeCount: number;
}

// Mock data - In production, fetch from /api/entities
const ENTITIES: EntityDef[] = [
  // D-FIN (Fiscus)
  { id: 'ENT-FIN-IPR', name: 'Intervención Pública Regional', domain: 'D-FIN', category: 'Master', attributeCount: 20 },
  { id: 'ENT-FIN-MECANISMO', name: 'Mecanismo de Financiamiento', domain: 'D-FIN', category: 'Reference', attributeCount: 8 },
  { id: 'ENT-FIN-ERD', name: 'Estrategia Regional de Desarrollo', domain: 'D-FIN', category: 'Master', attributeCount: 10 },
  { id: 'ENT-FIN-SERIE_FINANCIERA', name: 'Serie Financiera', domain: 'D-FIN', category: 'Transaction', attributeCount: 6 },
  { id: 'ENT-FIN-CONVENIO_PROGRAMACION', name: 'Convenio de Programación', domain: 'D-FIN', category: 'Transaction', attributeCount: 9 },
  // D-EJE (Actio)
  { id: 'ENT-EJE-CONVENIO', name: 'Convenio de Transferencia', domain: 'D-EJE', category: 'Transaction', attributeCount: 15 },
  { id: 'ENT-EJE-EJECUTOR', name: 'Ejecutor', domain: 'D-EJE', category: 'Master', attributeCount: 12 },
  { id: 'ENT-EJE-PROBLEMA', name: 'Problema de Ejecución', domain: 'D-EJE', category: 'Transaction', attributeCount: 14 },
  { id: 'ENT-EJE-CUOTA', name: 'Cuota de Pago', domain: 'D-EJE', category: 'Transaction', attributeCount: 10 },
  { id: 'ENT-EJE-BITACORA_OBRA', name: 'Bitácora de Obra', domain: 'D-EJE', category: 'Transaction', attributeCount: 8 },
  // D-CONV (Conventus)
  { id: 'ENT-CONV-SESION', name: 'Sesión', domain: 'D-CONV', category: 'Transaction', attributeCount: 10 },
  { id: 'ENT-CONV-INSTANCIA', name: 'Instancia Colectiva', domain: 'D-CONV', category: 'Master', attributeCount: 8 },
  { id: 'ENT-CONV-COMPROMISO', name: 'Compromiso', domain: 'D-CONV', category: 'Transaction', attributeCount: 14 },
  { id: 'ENT-CONV-PUNTO_TABLA', name: 'Punto de Tabla', domain: 'D-CONV', category: 'Transaction', attributeCount: 12 },
  { id: 'ENT-CONV-ACUERDO', name: 'Acuerdo', domain: 'D-CONV', category: 'Transaction', attributeCount: 8 },
  // D-ORG (Organicus)
  { id: 'ENT-ORG-FUNCIONARIO', name: 'Funcionario', domain: 'D-ORG', category: 'Master', attributeCount: 18 },
  { id: 'ENT-ORG-DIVISION', name: 'División', domain: 'D-ORG', category: 'Master', attributeCount: 6 },
  { id: 'ENT-ORG-CARGO', name: 'Cargo', domain: 'D-ORG', category: 'Reference', attributeCount: 5 },
  { id: 'ENT-ORG-REMUNERACION', name: 'Remuneración', domain: 'D-ORG', category: 'Transaction', attributeCount: 12 },
  // D-LOC (Locus)
  { id: 'ENT-LOC-COMUNA', name: 'Comuna', domain: 'D-LOC', category: 'Reference', attributeCount: 6 },
  { id: 'ENT-LOC-PROVINCIA', name: 'Provincia', domain: 'D-LOC', category: 'Reference', attributeCount: 4 },
  { id: 'ENT-LOC-ZONA_RIESGO', name: 'Zona de Riesgo', domain: 'D-LOC', category: 'Reference', attributeCount: 8 },
  { id: 'ENT-LOC-IPT', name: 'Instrumento de Planificación Territorial', domain: 'D-LOC', category: 'Master', attributeCount: 10 },
  // D-GEO (Geoespacial - Nuevo)
  { id: 'ENT-GEO-CAPA', name: 'Capa Geoespacial', domain: 'D-GEO', category: 'Master', attributeCount: 12 },
  { id: 'ENT-GEO-SERVICIO', name: 'Servicio OGC', domain: 'D-GEO', category: 'Reference', attributeCount: 8 },
  // D-SEG (Seguridad - Nuevo)
  { id: 'ENT-SEG-INCIDENTE', name: 'Incidente de Seguridad', domain: 'D-SEG', category: 'Transaction', attributeCount: 14 },
  { id: 'ENT-SEG-DISPOSITIVO', name: 'Dispositivo de Monitoreo', domain: 'D-SEG', category: 'Master', attributeCount: 10 },
  // D-DATA (Gobernanza - Nuevo)
  { id: 'ENT-DATA-ACTIVO', name: 'Activo de Información', domain: 'D-DATA', category: 'Master', attributeCount: 13 },
  // D-SAL (Salus)
  { id: 'ENT-SAL-ALERTA', name: 'Alerta', domain: 'D-SAL', category: 'Transaction', attributeCount: 12 },
  { id: 'ENT-SAL-PLAYBOOK', name: 'Playbook', domain: 'D-SAL', category: 'Reference', attributeCount: 8 },
  // D-GOV (Imperium)
  { id: 'ENT-GOV-SESION_CORE', name: 'Sesión CORE', domain: 'D-GOV', category: 'Transaction', attributeCount: 10 },
  { id: 'ENT-GOV-ACUERDO_CORE', name: 'Acuerdo CORE', domain: 'D-GOV', category: 'Transaction', attributeCount: 8 },
  // D-SYS (Nucleus)
  { id: 'ENT-SYS-DOCUMENTO', name: 'Documento', domain: 'D-SYS', category: 'Master', attributeCount: 10 },
  { id: 'ENT-SYS-ACTOR', name: 'Actor', domain: 'D-SYS', category: 'Master', attributeCount: 5 },
];

const DOMAIN_COLORS: Record<string, string> = {
  'D-FIN': 'bg-emerald-100 text-emerald-800 border-emerald-300',
  'D-EJE': 'bg-orange-100 text-orange-800 border-orange-300',
  'D-CONV': 'bg-blue-100 text-blue-800 border-blue-300',
  'D-ORG': 'bg-purple-100 text-purple-800 border-purple-300',
  'D-LOC': 'bg-teal-100 text-teal-800 border-teal-300',
  'D-GEO': 'bg-cyan-100 text-cyan-800 border-cyan-300',
  'D-SEG': 'bg-red-100 text-red-800 border-red-300',
  'D-DATA': 'bg-indigo-100 text-indigo-800 border-indigo-300',
  'D-SAL': 'bg-rose-100 text-rose-800 border-rose-300',
  'D-GOV': 'bg-amber-100 text-amber-800 border-amber-300',
  'D-SYS': 'bg-gray-100 text-gray-800 border-gray-300',
};

const DOMAIN_NAMES: Record<string, string> = {
  'D-FIN': 'Fiscus (Finanzas)',
  'D-EJE': 'Actio (Ejecución)',
  'D-CONV': 'Conventus (Convergencia)',
  'D-ORG': 'Organicus (Organización)',
  'D-LOC': 'Locus (Territorio)',
  'D-GEO': 'Geoespacial',
  'D-SEG': 'Seguridad',
  'D-DATA': 'Gobernanza de Datos',
  'D-SAL': 'Salus (Salud Institucional)',
  'D-GOV': 'Imperium (Gobierno)',
  'D-SYS': 'Nucleus (Sistema)',
};

export function EntityExplorer() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const domains = useMemo(() => [...new Set(ENTITIES.map(e => e.domain))].sort(), []);
  const categories = useMemo(() => [...new Set(ENTITIES.map(e => e.category))].sort(), []);

  const filteredEntities = useMemo(() => {
    return ENTITIES.filter(entity => {
      const matchesSearch = 
        entity.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entity.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesDomain = !selectedDomain || entity.domain === selectedDomain;
      const matchesCategory = !selectedCategory || entity.category === selectedCategory;
      return matchesSearch && matchesDomain && matchesCategory;
    });
  }, [searchTerm, selectedDomain, selectedCategory]);

  const stats = useMemo(() => {
    const byDomain = domains.reduce((acc, d) => {
      acc[d] = ENTITIES.filter(e => e.domain === d).length;
      return acc;
    }, {} as Record<string, number>);
    return { total: ENTITIES.length, byDomain };
  }, [domains]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-800">
                GORE_OS <span className="text-slate-400 font-normal">| Entity Explorer</span>
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                {stats.total} entidades · 11 dominios · Ontología Categórica v4.1
              </p>
            </div>
            <div className="flex gap-3">
              <a href="#ipr" className="px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 transition-colors">
                📊 Portafolio IPR
              </a>
              <a href="#crisis" className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors">
                🚨 Centro de Crisis
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Search & Filters */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Buscar entidad por ID o nombre..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-lg"
              />
              <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>

            {/* Domain Filter */}
            <select
              value={selectedDomain || ''}
              onChange={(e) => setSelectedDomain(e.target.value || null)}
              className="px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
            >
              <option value="">Todos los dominios</option>
              {domains.map(d => (
                <option key={d} value={d}>{d} ({stats.byDomain[d]})</option>
              ))}
            </select>

            {/* Category Filter */}
            <select
              value={selectedCategory || ''}
              onChange={(e) => setSelectedCategory(e.target.value || null)}
              className="px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
            >
              <option value="">Todas las categorías</option>
              {categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Quick Stats */}
          <div className="flex flex-wrap gap-2 mt-4">
            {domains.map(domain => (
              <button
                key={domain}
                onClick={() => setSelectedDomain(selectedDomain === domain ? null : domain)}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-all ${
                  selectedDomain === domain 
                    ? 'ring-2 ring-offset-1 ring-slate-400' 
                    : 'hover:scale-105'
                } ${DOMAIN_COLORS[domain]}`}
              >
                {domain} ({stats.byDomain[domain]})
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-700">
            {filteredEntities.length} entidades encontradas
          </h2>
          {(searchTerm || selectedDomain || selectedCategory) && (
            <button
              onClick={() => { setSearchTerm(''); setSelectedDomain(null); setSelectedCategory(null); }}
              className="text-sm text-slate-500 hover:text-slate-700 underline"
            >
              Limpiar filtros
            </button>
          )}
        </div>

        {/* Entity Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredEntities.map(entity => (
            <div
              key={entity.id}
              className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-lg hover:border-slate-300 transition-all group cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <span className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${DOMAIN_COLORS[entity.domain]}`}>
                  {entity.domain}
                </span>
                <span className="text-xs text-slate-400 font-mono group-hover:text-slate-600">
                  {entity.attributeCount} attrs
                </span>
              </div>
              <h3 className="font-semibold text-slate-800 mb-1 group-hover:text-emerald-700">
                {entity.name}
              </h3>
              <p className="text-xs font-mono text-slate-500 mb-2">{entity.id}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">{entity.category}</span>
                <span className="text-xs text-slate-300">{DOMAIN_NAMES[entity.domain]}</span>
              </div>
            </div>
          ))}
        </div>

        {filteredEntities.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl border border-slate-200">
            <p className="text-slate-500 text-lg">No se encontraron entidades con esos criterios.</p>
            <button
              onClick={() => { setSearchTerm(''); setSelectedDomain(null); setSelectedCategory(null); }}
              className="mt-4 text-emerald-600 hover:underline"
            >
              Mostrar todas las entidades
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            GORE_OS v2.2 · Modelo Categórico · {new Date().toLocaleDateString('es-CL')}
          </p>
          <div className="flex gap-4 text-sm text-slate-500">
            <a href="#ui" className="hover:text-slate-700">UI Showcase</a>
            <a href="https://github.com/gore-nuble" className="hover:text-slate-700">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

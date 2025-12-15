// GORE_OS - Seed de Datos Maestros
// Generado desde artefactos KODA
// Fecha: 2024-12-14

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Iniciando seed de datos maestros GORE_OS...')

  // ═══════════════════════════════════════════════════════════════════════════
  // TERRITORIOS (Región de Ñuble)
  // ═══════════════════════════════════════════════════════════════════════════
  console.log('📍 Creando territorios...')

  const chile = await prisma.territorio.upsert({
    where: { codigoCut: 'CL' },
    update: {},
    create: {
      codigoCut: 'CL',
      nombre: 'Chile',
      nombreOficial: 'República de Chile',
      tipo: 'PAIS',
      activo: true,
    },
  })

  const nuble = await prisma.territorio.upsert({
    where: { codigoCut: '16' },
    update: {},
    create: {
      codigoCut: '16',
      nombre: 'Ñuble',
      nombreOficial: 'Región de Ñuble',
      tipo: 'REGION',
      parentId: chile.id,
      superficieKm2: 13178.5,
      poblacion: 480609,
      anioPoblacion: 2017,
      activo: true,
    },
  })

  // Provincias
  const provincias = [
    { codigo: '161', nombre: 'Diguillín', capital: true },
    { codigo: '162', nombre: 'Itata', capital: false },
    { codigo: '163', nombre: 'Punilla', capital: false },
  ]

  const provinciasCreadas: Record<string, any> = {}
  for (const prov of provincias) {
    provinciasCreadas[prov.codigo] = await prisma.territorio.upsert({
      where: { codigoCut: prov.codigo },
      update: {},
      create: {
        codigoCut: prov.codigo,
        nombre: prov.nombre,
        tipo: 'PROVINCIA',
        parentId: nuble.id,
        activo: true,
      },
    })
  }

  // Comunas
  const comunas = [
    // Diguillín
    { codigo: '16101', nombre: 'Chillán', provincia: '161', capital: true, poblacion: 184739 },
    { codigo: '16102', nombre: 'Bulnes', provincia: '161', capital: false, poblacion: 22254 },
    { codigo: '16103', nombre: 'Chillán Viejo', provincia: '161', capital: false, poblacion: 33876 },
    { codigo: '16104', nombre: 'El Carmen', provincia: '161', capital: false, poblacion: 12469 },
    { codigo: '16105', nombre: 'Pemuco', provincia: '161', capital: false, poblacion: 8076 },
    { codigo: '16106', nombre: 'Pinto', provincia: '161', capital: false, poblacion: 11561 },
    { codigo: '16107', nombre: 'Quillón', provincia: '161', capital: false, poblacion: 16234 },
    { codigo: '16108', nombre: 'San Ignacio', provincia: '161', capital: false, poblacion: 15208 },
    { codigo: '16109', nombre: 'Yungay', provincia: '161', capital: false, poblacion: 18358 },
    // Itata
    { codigo: '16201', nombre: 'Quirihue', provincia: '162', capital: false, poblacion: 12233 },
    { codigo: '16202', nombre: 'Cobquecura', provincia: '162', capital: false, poblacion: 5335 },
    { codigo: '16203', nombre: 'Coelemu', provincia: '162', capital: false, poblacion: 17219 },
    { codigo: '16204', nombre: 'Ninhue', provincia: '162', capital: false, poblacion: 5593 },
    { codigo: '16205', nombre: 'Portezuelo', provincia: '162', capital: false, poblacion: 5195 },
    { codigo: '16206', nombre: 'Ránquil', provincia: '162', capital: false, poblacion: 5956 },
    { codigo: '16207', nombre: 'Trehuaco', provincia: '162', capital: false, poblacion: 5008 },
    // Punilla
    { codigo: '16301', nombre: 'San Carlos', provincia: '163', capital: false, poblacion: 53913 },
    { codigo: '16302', nombre: 'Coihueco', provincia: '163', capital: false, poblacion: 26063 },
    { codigo: '16303', nombre: 'Ñiquén', provincia: '163', capital: false, poblacion: 11670 },
    { codigo: '16304', nombre: 'San Fabián', provincia: '163', capital: false, poblacion: 3820 },
    { codigo: '16305', nombre: 'San Nicolás', provincia: '163', capital: false, poblacion: 11431 },
  ]

  for (const comuna of comunas) {
    await prisma.territorio.upsert({
      where: { codigoCut: comuna.codigo },
      update: {},
      create: {
        codigoCut: comuna.codigo,
        nombre: comuna.nombre,
        tipo: 'COMUNA',
        parentId: provinciasCreadas[comuna.provincia].id,
        esCapitalRegional: comuna.capital,
        poblacion: comuna.poblacion,
        anioPoblacion: 2017,
        activo: true,
      },
    })
  }

  console.log(`   ✓ ${comunas.length + provincias.length + 2} territorios creados`)

  // ═══════════════════════════════════════════════════════════════════════════
  // PERÍODOS
  // ═══════════════════════════════════════════════════════════════════════════
  console.log('📅 Creando períodos...')

  const anios = [2024, 2025]
  for (const anio of anios) {
    await prisma.periodo.upsert({
      where: { codigo: `A${anio}` },
      update: {},
      create: {
        codigo: `A${anio}`,
        tipo: 'ANUAL',
        anio: anio,
        fechaInicio: new Date(`${anio}-01-01`),
        fechaFin: new Date(`${anio}-12-31`),
        esActual: anio === 2025,
      },
    })

    // Trimestres
    for (let q = 1; q <= 4; q++) {
      const mesInicio = (q - 1) * 3 + 1
      const mesFin = q * 3
      await prisma.periodo.upsert({
        where: { codigo: `Q${q}-${anio}` },
        update: {},
        create: {
          codigo: `Q${q}-${anio}`,
          tipo: 'TRIMESTRE',
          anio: anio,
          trimestre: q,
          fechaInicio: new Date(`${anio}-${String(mesInicio).padStart(2, '0')}-01`),
          fechaFin: new Date(`${anio}-${String(mesFin).padStart(2, '0')}-${mesFin === 2 ? 28 : [4,6,9,11].includes(mesFin) ? 30 : 31}`),
          esActual: anio === 2025 && q === 1,
        },
      })
    }
  }

  console.log('   ✓ Períodos creados')

  // ═══════════════════════════════════════════════════════════════════════════
  // UNIDADES ORGÁNICAS
  // ═══════════════════════════════════════════════════════════════════════════
  console.log('🏛️ Creando unidades orgánicas...')

  const gabinete = await prisma.unidadOrganica.upsert({
    where: { codigo: 'GAB' },
    update: {},
    create: {
      codigo: 'GAB',
      nombre: 'Gabinete del Gobernador',
      sigla: 'GAB',
      tipo: 'GABINETE',
      nivel: 1,
      orden: 1,
      activo: true,
    },
  })

  const divisiones = [
    { codigo: 'DIPLADE', nombre: 'División de Planificación y Desarrollo', sigla: 'DIPLADE', orden: 2 },
    { codigo: 'DAF', nombre: 'División de Administración y Finanzas', sigla: 'DAF', orden: 3 },
    { codigo: 'DIFOP', nombre: 'División de Fomento Productivo', sigla: 'DIFOP', orden: 4 },
    { codigo: 'DIDES', nombre: 'División de Desarrollo Social', sigla: 'DIDES', orden: 5 },
    { codigo: 'DINFRA', nombre: 'División de Infraestructura y Transportes', sigla: 'DINFRA', orden: 6 },
  ]

  for (const div of divisiones) {
    await prisma.unidadOrganica.upsert({
      where: { codigo: div.codigo },
      update: {},
      create: {
        codigo: div.codigo,
        nombre: div.nombre,
        sigla: div.sigla,
        tipo: 'DIVISION',
        nivel: 2,
        parentId: gabinete.id,
        orden: div.orden,
        activo: true,
      },
    })
  }

  console.log(`   ✓ ${divisiones.length + 1} unidades orgánicas creadas`)

  // ═══════════════════════════════════════════════════════════════════════════
  // INSTRUMENTOS DE FINANCIAMIENTO
  // ═══════════════════════════════════════════════════════════════════════════
  console.log('💰 Creando instrumentos de financiamiento...')

  const instrumentos = [
    { codigo: 'FNDR', nombre: 'Fondo Nacional de Desarrollo Regional', tipo: 'FNDR', subtipo: '31', requiereRs: true, requiereCore: true },
    { codigo: 'FRIL', nombre: 'Fondo Regional de Iniciativa Local', tipo: 'FRIL', subtipo: '31', requiereRs: true, requiereCore: true, montoMax: 120000000 },
    { codigo: 'PMU', nombre: 'Programa de Mejoramiento Urbano', tipo: 'PMU', subtipo: '31', requiereRs: true, requiereCore: true },
    { codigo: 'PMB', nombre: 'Programa de Mejoramiento de Barrios', tipo: 'PMB', subtipo: '31', requiereRs: true, requiereCore: true },
    { codigo: 'FRPD', nombre: 'Fondo Regional de Protección del Patrimonio', tipo: 'FRPD', subtipo: '31', requiereRs: false, requiereCore: true },
    { codigo: 'SUB8', nombre: 'Subvención Art. 8%', tipo: 'SUBVENCION', subtipo: '24', requiereRs: false, requiereCore: true },
    { codigo: 'FIC', nombre: 'Fondo de Innovación para la Competitividad', tipo: 'FIC', subtipo: '31', requiereRs: false, requiereCore: true },
    { codigo: 'FAGEM', nombre: 'Fondo de Apoyo a Gestión de Emergencias', tipo: 'FAGEM', subtipo: '33', requiereRs: false, requiereCore: false },
  ]

  for (const inst of instrumentos) {
    await prisma.instrumentoFinanciamiento.upsert({
      where: { codigo: inst.codigo },
      update: {},
      create: {
        codigo: inst.codigo,
        nombre: inst.nombre,
        nombreCorto: inst.codigo,
        tipo: inst.tipo as any,
        subtipoPresup: inst.subtipo,
        requiereRs: inst.requiereRs,
        requiereCore: inst.requiereCore,
        montoMaximo: inst.montoMax || null,
        vigente: true,
      },
    })
  }

  console.log(`   ✓ ${instrumentos.length} instrumentos creados`)

  // ═══════════════════════════════════════════════════════════════════════════
  // ROLES
  // ═══════════════════════════════════════════════════════════════════════════
  console.log('🔐 Creando roles...')

  const roles = [
    { codigo: 'SUPER_ADMIN', nombre: 'Super Administrador', permisos: ['*'], esSistema: true },
    { codigo: 'GOBERNADOR', nombre: 'Gobernador Regional', permisos: ['plan:*:read', 'fin:*:read', 'ejec:*:read', 'gestion:*'] },
    { codigo: 'JEFE_DIPLADE', nombre: 'Jefe DIPLADE', permisos: ['plan:*', 'fin:iniciativa:read', 'gestion:okr:*'] },
    { codigo: 'JEFE_DAF', nombre: 'Jefe DAF', permisos: ['fin:*', 'ejec:*', 'gestion:okr:*'] },
    { codigo: 'ANALISTA_IPR', nombre: 'Analista IPR', permisos: ['fin:iniciativa:*', 'fin:solicitud:*', 'ejec:convenio:*'] },
    { codigo: 'ANALISTA_REND', nombre: 'Analista Rendiciones', permisos: ['ejec:convenio:read', 'ejec:rendicion:*'] },
    { codigo: 'SUPERVISOR_TEC', nombre: 'Supervisor Técnico', permisos: ['ejec:convenio:read', 'ejec:hito:*', 'ejec:pmo:update'] },
    { codigo: 'PMO_MANAGER', nombre: 'PMO Manager', permisos: ['ejec:convenio:read', 'ejec:pmo:*', 'gestion:alerta:manage'] },
    { codigo: 'CONTROLLER', nombre: 'Controller Gestión', permisos: ['gestion:*', 'fin:presupuesto:read', 'ejec:pmo:read'] },
    { codigo: 'USUARIO_MUNICIPAL', nombre: 'Usuario Municipal', permisos: ['fin:iniciativa:read_own', 'fin:solicitud:*_own', 'ejec:convenio:read_own', 'ejec:rendicion:*_own'] },
    { codigo: 'CONSULTA', nombre: 'Solo Consulta', permisos: ['plan:erd:read', 'plan:prot:read', 'fin:presupuesto:read'] },
  ]

  for (const rol of roles) {
    await prisma.rol.upsert({
      where: { codigo: rol.codigo },
      update: {},
      create: {
        codigo: rol.codigo,
        nombre: rol.nombre,
        permisos: rol.permisos,
        esSistema: rol.esSistema || false,
        activo: true,
      },
    })
  }

  console.log(`   ✓ ${roles.length} roles creados`)

  // ═══════════════════════════════════════════════════════════════════════════
  // ACTORES (Municipalidades)
  // ═══════════════════════════════════════════════════════════════════════════
  console.log('🏢 Creando actores (municipalidades)...')

  const municipalidades = [
    { rut: '69.150.300-3', nombre: 'Municipalidad de Chillán', comuna: '16101' },
    { rut: '69.150.400-K', nombre: 'Municipalidad de Bulnes', comuna: '16102' },
    { rut: '69.150.500-6', nombre: 'Municipalidad de Chillán Viejo', comuna: '16103' },
    { rut: '69.150.600-2', nombre: 'Municipalidad de El Carmen', comuna: '16104' },
    { rut: '69.150.700-9', nombre: 'Municipalidad de Pemuco', comuna: '16105' },
    { rut: '69.150.800-5', nombre: 'Municipalidad de Pinto', comuna: '16106' },
    { rut: '69.150.900-1', nombre: 'Municipalidad de Quillón', comuna: '16107' },
    { rut: '69.151.000-4', nombre: 'Municipalidad de San Ignacio', comuna: '16108' },
    { rut: '69.151.100-0', nombre: 'Municipalidad de Yungay', comuna: '16109' },
    { rut: '69.151.200-7', nombre: 'Municipalidad de Quirihue', comuna: '16201' },
    { rut: '69.151.300-3', nombre: 'Municipalidad de Cobquecura', comuna: '16202' },
    { rut: '69.151.400-K', nombre: 'Municipalidad de Coelemu', comuna: '16203' },
    { rut: '69.151.500-6', nombre: 'Municipalidad de Ninhue', comuna: '16204' },
    { rut: '69.151.600-2', nombre: 'Municipalidad de Portezuelo', comuna: '16205' },
    { rut: '69.151.700-9', nombre: 'Municipalidad de Ránquil', comuna: '16206' },
    { rut: '69.151.800-5', nombre: 'Municipalidad de Trehuaco', comuna: '16207' },
    { rut: '69.151.900-1', nombre: 'Municipalidad de San Carlos', comuna: '16301' },
    { rut: '69.152.000-4', nombre: 'Municipalidad de Coihueco', comuna: '16302' },
    { rut: '69.152.100-0', nombre: 'Municipalidad de Ñiquén', comuna: '16303' },
    { rut: '69.152.200-7', nombre: 'Municipalidad de San Fabián', comuna: '16304' },
    { rut: '69.152.300-3', nombre: 'Municipalidad de San Nicolás', comuna: '16305' },
  ]

  for (const muni of municipalidades) {
    const territorio = await prisma.territorio.findUnique({ where: { codigoCut: muni.comuna } })
    await prisma.actor.upsert({
      where: { rut: muni.rut },
      update: {},
      create: {
        rut: muni.rut,
        nombre: muni.nombre,
        nombreCorto: muni.nombre.replace('Municipalidad de ', 'Mun. '),
        tipo: 'MUNICIPALIDAD',
        territorioId: territorio?.id,
        esUnidadEjecutora: true,
        esBeneficiario: true,
        clasificacionUE: 'SIN_CLASIFICAR',
        activo: true,
      },
    })
  }

  console.log(`   ✓ ${municipalidades.length} municipalidades creadas`)

  // ═══════════════════════════════════════════════════════════════════════════
  console.log('')
  console.log('✅ Seed completado exitosamente!')
  console.log('')
}

main()
  .catch((e) => {
    console.error('❌ Error en seed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })

import { iprConfig } from "./ipr";
import { indicadoresConfig } from "./indicadores";
import { presupuestoConfig } from "./presupuesto";
import { conveniosConfig } from "./convenios";
import { organizacionesConfig } from "./organizaciones";
import { personasConfig } from "./personas";
import { territorioConfig } from "./territorio";
import { eventosConfig } from "./eventos";
import { rendicionesConfig } from "./rendiciones";
import type { DomainConfig } from "./types";

export const domainRegistry: Record<string, DomainConfig> = {
  ipr: iprConfig,
  indicadores: indicadoresConfig,
  presupuesto: presupuestoConfig,
  convenios: conveniosConfig,
  organizaciones: organizacionesConfig,
  personas: personasConfig,
  territorio: territorioConfig,
  eventos: eventosConfig,
  rendiciones: rendicionesConfig,
};

export type { DomainConfig } from "./types";

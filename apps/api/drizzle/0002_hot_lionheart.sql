ALTER TABLE "fin_fondo" ADD COLUMN "codigo" text NOT NULL;--> statement-breakpoint
ALTER TABLE "fin_fondo" ADD COLUMN "nombre" text NOT NULL;--> statement-breakpoint
ALTER TABLE "fin_fondo" ADD COLUMN "descripcion" text NOT NULL;--> statement-breakpoint
ALTER TABLE "fin_fondo" ADD COLUMN "normativa_base" text NOT NULL;--> statement-breakpoint
ALTER TABLE "fin_fondo" ADD COLUMN "vigente" boolean NOT NULL;--> statement-breakpoint
ALTER TABLE "fin_fondo" ADD COLUMN "requiere_aporte_propio" boolean NOT NULL;
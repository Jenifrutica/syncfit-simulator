import { existsSync, readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const TELEMETRY_SCHEMA_ID = "https://syncfit.edge/schemas/telemetry-frame.schema.json";

export type ValidateFn = (data: unknown) => boolean;

/** Locate the contracts schema directory (env override or sibling repo). */
export function resolveSchemaDir(): string | null {
  const candidates = [
    process.env.SYNCFIT_SCHEMA_DIR,
    resolve(process.cwd(), "../syncfit-contracts/schemas"),
    resolve(process.cwd(), "../../syncfit-contracts/schemas"),
    resolve(process.cwd(), "schemas"),
  ].filter((value): value is string => Boolean(value));

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

/**
 * Build a telemetry-frame validator from the JSON Schemas in the contracts
 * repository. Returns null when the schemas are not available.
 */
export function createTelemetryValidator(schemaDir?: string): ValidateFn | null {
  const dir = schemaDir ?? resolveSchemaDir();
  if (!dir) {
    return null;
  }
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  for (const file of readdirSync(dir)) {
    if (!file.endsWith(".schema.json")) {
      continue;
    }
    const schema = JSON.parse(readFileSync(resolve(dir, file), "utf-8"));
    ajv.addSchema(schema, schema.$id ?? file);
  }
  const validator = ajv.getSchema(TELEMETRY_SCHEMA_ID);
  if (!validator) {
    return null;
  }
  return (data: unknown) => Boolean(validator(data));
}

/** Validate a frame and throw with a clear message when invalid. */
export function assertValidFrame(frame: unknown, schemaDir?: string): void {
  const validator = createTelemetryValidator(schemaDir);
  if (!validator) {
    throw new Error(
      "contract schemas not found; set SYNCFIT_SCHEMA_DIR to syncfit-contracts/schemas",
    );
  }
  if (!validator(frame)) {
    throw new Error("telemetry frame does not match the contract");
  }
}

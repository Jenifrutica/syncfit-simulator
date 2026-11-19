import { existsSync, readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import type { ValidateFunction } from "ajv";
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

function compile(dir: string): ValidateFunction | null {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  for (const file of readdirSync(dir)) {
    if (!file.endsWith(".schema.json")) {
      continue;
    }
    const schema = JSON.parse(readFileSync(resolve(dir, file), "utf-8"));
    ajv.addSchema(schema, schema.$id ?? file);
  }
  return ajv.getSchema(TELEMETRY_SCHEMA_ID) ?? null;
}

// Reading and compiling ~30 schemas per frame is wasteful: a session validates
// every frame it generates, so keep one compiled validator per directory.
const compiled = new Map<string, ValidateFunction | null>();

function telemetryValidator(schemaDir?: string): ValidateFunction | null {
  const dir = schemaDir ?? resolveSchemaDir();
  if (!dir) {
    return null;
  }
  if (!compiled.has(dir)) {
    compiled.set(dir, compile(dir));
  }
  return compiled.get(dir) ?? null;
}

/**
 * Build a telemetry-frame validator from the JSON Schemas in the contracts
 * repository. Returns null when the schemas are not available.
 */
export function createTelemetryValidator(schemaDir?: string): ValidateFn | null {
  const validator = telemetryValidator(schemaDir);
  return validator ? (data: unknown) => Boolean(validator(data)) : null;
}

/** Validate a frame and throw with a clear message when invalid. */
export function assertValidFrame(frame: unknown, schemaDir?: string): void {
  const validator = telemetryValidator(schemaDir);
  if (!validator) {
    throw new Error(
      "contract schemas not found; set SYNCFIT_SCHEMA_DIR to syncfit-contracts/schemas",
    );
  }
  if (!validator(frame)) {
    const detail = (validator.errors ?? [])
      .map((error) => `${error.instancePath || "/"} ${error.message ?? "is invalid"}`)
      .join("; ");
    throw new Error(
      `telemetry frame does not match the contract${detail ? `: ${detail}` : ""}`,
    );
  }
}

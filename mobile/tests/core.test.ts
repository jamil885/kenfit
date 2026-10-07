import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { numeric, optionalNumber, validDate, today } from "../src/lib/utils";
import {
  request,
  configureApi,
  ApiError,
  allPages,
  errorDetail,
} from "../src/lib/api";
import { resetDemo, demoRequest } from "../src/lib/demo";
import type { Meal, DaySummary, WorkoutLog, Workout } from "../src/types";
const originalFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = originalFetch;
  configureApi(null, false);
});

test("local calendar dates reject impossible and future dates", () => {
  assert.equal(validDate("2024-02-29"), "2024-02-29");
  assert.throws(() => validDate("2025-02-29"));
  assert.throws(() => validDate("2026-13-01"));
  assert.throws(() => validDate("2099-01-01"));
  assert.throws(() => validDate(today(), true));
});

test("quantities accept decimal commas but reject empty, nonfinite and fractional sets", () => {
  assert.equal(numeric("1,5", "Porción", 0.1, 100), 1.5);
  assert.equal(optionalNumber("", "Carga", 0, 100), undefined);
  assert.equal(numeric("0", "Carga", 0, 100), 0);
  assert.throws(() => numeric("", "Cantidad", 0, 100));
  assert.throws(() => numeric("Infinity", "Cantidad", 0, 100));
  assert.throws(() => numeric("1.5", "Series", 1, 100, true));
});

test("API sends bearer and strips undefined optional payload fields", async () => {
  configureApi("secret-for-test", false);
  globalThis.fetch = async (_url, options) => {
    assert.equal(
      (options?.headers as Record<string, string>).Authorization,
      "Bearer secret-for-test",
    );
    assert.equal(options?.body, JSON.stringify({ grams: 100 }));
    return new Response(JSON.stringify({ ok: true }), { status: 201 });
  };
  assert.deepEqual(
    await request("/test", {
      method: "POST",
      body: { grams: 100, servings: undefined },
    }),
    { ok: true },
  );
});

test("401 clears session once and reports expiry", async () => {
  let expired = 0;
  configureApi("test", false, () => {
    expired++;
    configureApi(null, false);
  });
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Invalid token" }), { status: 401 });
  await assert.rejects(
    request("/private"),
    (e: unknown) => e instanceof ApiError && e.status === 401,
  );
  assert.equal(expired, 1);
});

test("failed login does not expire an unrelated session callback", async () => {
  let expired = 0;
  configureApi(null, false, () => expired++);
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Invalid email or password" }), {
      status: 401,
    });
  await assert.rejects(request("/auth/login"), /Correo o contraseña/);
  assert.equal(expired, 0);
});

test("network errors do not expose internal payloads", async () => {
  configureApi(null, false);
  globalThis.fetch = async () => {
    throw new Error("internal detail");
  };
  await assert.rejects(request("/health"), /No se pudo conectar/);
});

test("204 has no JSON body and pagination retrieves beyond first 100 entries", async () => {
  let calls = 0;
  globalThis.fetch = async (url) => {
    calls++;
    if (String(url).endsWith("/delete"))
      return new Response(null, { status: 204 });
    const offset = new URL(String(url)).searchParams.get("offset");
    return new Response(
      JSON.stringify(
        offset === "0"
          ? Array.from({ length: 100 }, (_, i) => ({ id: i }))
          : [{ id: 100 }],
      ),
      { status: 200 },
    );
  };
  assert.equal(await request("/delete", { method: "DELETE" }), undefined);
  const values = await allPages<{ id: number }>("/items");
  assert.equal(values.length, 101);
  assert.equal(calls, 3);
});

test("validation details preserve field names", () => {
  assert.match(
    errorDetail([{ loc: ["body", "weight_kg"], msg: "invalid" }]),
    /weight_kg/,
  );
});

test("demo never touches network and state resets between demo sessions", async () => {
  resetDemo();
  configureApi("demo", true);
  globalThis.fetch = async () => {
    throw new Error("Network must not be used");
  };
  const before = await request<DaySummary>(
    "/nutrition/summary?recorded_on=" + today(),
  );
  await request("/nutrition/meals", {
    method: "POST",
    body: { food_id: 1, recorded_on: today(), meal: "dinner", grams: 100 },
  });
  assert.equal(
    (await request<DaySummary>("/nutrition/summary?recorded_on=" + today()))
      .entries.length,
    before.entries.length + 1,
  );
  resetDemo();
  assert.equal(
    (await request<DaySummary>("/nutrition/summary?recorded_on=" + today()))
      .entries.length,
    before.entries.length,
  );
});

test("demo meal grams and servings produce equivalent nutrition", async () => {
  resetDemo();
  const base = { food_id: 1, recorded_on: today(), meal: "lunch" };
  const grams = (await demoRequest("/nutrition/meals", "POST", {
    ...base,
    grams: 150,
  })) as Meal;
  const servings = (await demoRequest("/nutrition/meals", "POST", {
    ...base,
    servings: 1,
  })) as Meal;
  assert.equal(grams.calories, servings.calories);
  assert.equal(grams.grams, 150);
});

test("demo log keeps prescription snapshot when recorded", async () => {
  resetDemo();
  const w = (await demoRequest("/workouts/1", "GET")) as Workout;
  const log = (await demoRequest("/workout-logs", "POST", {
    workout_id: w.id,
    performed_on: today(),
    status: "partial",
    results: [{ position: 1, set_number: 1, reps: 7 }],
  })) as WorkoutLog;
  assert.equal(log.results[0]?.prescribed_reps, 8);
  assert.equal(log.results[0]?.reps, 7);
});

const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const project = path.resolve(__dirname, "../..");
const output = project + "/docs/mobile/screenshots";
fs.mkdirSync(output, { recursive: true });
const errors = [];
const os = require("os");
const net = require("net");
const { spawnSync } = require("child_process");
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "kenfit-mobile-e2e-"));
const python =
  process.env.KENFIT_PYTHON ||
  path.join(
    project,
    "backend",
    ".venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
  );
let backend, web, apiUrl, webUrl;
const freePort = () =>
  new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
async function setup() {
  const apiPort = await freePort(),
    webPort = await freePort();
  apiUrl = `http://127.0.0.1:${apiPort}`;
  webUrl = `http://127.0.0.1:${webPort}`;
  const env = {
    ...process.env,
    DATABASE_URL: "sqlite:///" + path.join(temp, "test.db").replace(/\\/g, "/"),
    JWT_SECRET_KEY: "test-integration-secret-at-least-32-characters",
    CORS_ORIGINS: JSON.stringify([webUrl]),
  };
  for (const args of [
    ["-m", "alembic", "upgrade", "head"],
    ["-m", "app.seed"],
  ]) {
    const result = spawnSync(python, args, {
      cwd: project + "/backend",
      env,
      encoding: "utf8",
    });
    if (result.status !== 0)
      throw new Error(
        result.stderr ||
          result.error?.message ||
          "Unable to initialize isolated test backend",
      );
  }
  const expo = path.join(
    path.dirname(require.resolve("expo/package.json")),
    "bin",
    "cli",
  );
  const built = spawnSync(
    process.execPath,
    [
      expo,
      "export",
      "--platform",
      "web",
      "--clear",
      "--output-dir",
      "dist-e2e",
      "--max-workers",
      "2",
    ],
    {
      cwd: project + "/mobile",
      env: {
        ...process.env,
        CI: "1",
        EXPO_OFFLINE: "1",
        EXPO_PUBLIC_API_URL: apiUrl,
      },
      encoding: "utf8",
      maxBuffer: 10 * 1024 * 1024,
    },
  );
  if (built.status !== 0)
    throw new Error(built.stderr || "Unable to build test frontend");
  backend = spawn(
    python,
    [
      "-m",
      "uvicorn",
      "app.app.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      String(apiPort),
    ],
    { cwd: project + "/backend", env, stdio: ["ignore", "ignore", "pipe"] },
  );
  web = spawn(
    python,
    ["-m", "http.server", String(webPort), "--bind", "127.0.0.1"],
    { cwd: project + "/mobile/dist-e2e", stdio: "ignore" },
  );
  backend.stderr.on("data", (d) => {
    if (String(d).includes("ERROR")) console.log(String(d));
  });
}
const delay = (ms) => new Promise((r) => setTimeout(r, ms));
async function ready(url) {
  for (let i = 0; i < 60; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch {}
    await delay(250);
  }
  throw new Error("Not ready: " + url);
}
(async () => {
  let browser;
  try {
    await setup();
    await ready(apiUrl + "/health");
    await ready(webUrl);
    browser = await chromium.launch({
      headless: true,
      ...(process.env.KENFIT_BROWSER_EXECUTABLE
        ? {
            executablePath: process.env.KENFIT_BROWSER_EXECUTABLE,
            args: [
              "--no-sandbox",
              "--single-process",
              "--no-zygote",
              "--disable-gpu",
            ],
          }
        : {}),
    });
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(webUrl);
    await page
      .getByRole("button", { name: "Explorar demostración", exact: true })
      .waitFor();
    await page.screenshot({ path: output + "/01-acceso.png" });
    await page
      .getByRole("button", { name: "Explorar demostración", exact: true })
      .click();
    await page.getByText("Hola, Kenji ✦", { exact: true }).waitFor();
    await page
      .getByRole("button", { name: "Ver mi plan", exact: true })
      .waitFor();
    await page.screenshot({ path: output + "/02-inicio.png" });
    console.log("Demo startup works");
    console.log((await page.getByRole("tab").allTextContents()).join("|"));
    await page.getByRole("tab", { name: "Entreno" }).click();
    await page.getByText("Muévete con intención", { exact: true }).waitFor();
    await page.screenshot({ path: output + "/03-entrenamiento.png" });
    await page.getByRole("tab", { name: "Nutrición" }).click();
    await page.getByText("Dale energía a tu día", { exact: true }).waitFor();
    await page
      .getByRole("button", { name: "Registrar comida", exact: true })
      .waitFor();
    await page.screenshot({ path: output + "/04-nutricion.png" });
    await page
      .getByRole("button", { name: "Registrar comida", exact: true })
      .click();
    await page.getByText("Banana", { exact: true }).click();
    await page
      .getByRole("textbox", { name: "Cantidad (g)", exact: true })
      .fill("200");
    await page
      .getByRole("button", { name: "Guardar comida", exact: true })
      .click();
    await page.getByText("Dale energía a tu día", { exact: true }).waitFor();
    await page.getByText("Banana", { exact: true }).waitFor();
    console.log("Demo meal saved");
    await page.getByRole("tab", { name: "Progreso" }).click();
    await page.getByText("Mira cuánto has avanzado", { exact: true }).waitFor();
    await page
      .getByText(
        "Escala relativa entre registros; las barras no parten de cero. El peso es solo una parte de tu progreso.",
        { exact: true },
      )
      .waitFor();
    await page.screenshot({ path: output + "/05-progreso.png" });
    await page.getByRole("tab", { name: "Perfil" }).click();
    await page
      .getByRole("button", { name: "Cerrar sesión", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Regístrate", exact: false })
      .count()
      .then(async (n) => {
        if (n)
          await page.getByRole("button", { name: /Primera vez aquí/ }).click();
        else await page.getByText("Regístrate", { exact: false }).click();
      });
    const email = "mobile-" + Date.now() + "@example.com";
    await page
      .getByRole("textbox", { name: "Nombre", exact: true })
      .fill("Atleta de prueba");
    await page
      .getByRole("textbox", { name: "Correo electrónico", exact: true })
      .fill(email);
    await page
      .getByRole("textbox", { name: "Contraseña", exact: true })
      .fill("Integration123!");
    await page
      .getByRole("button", { name: "Crear cuenta", exact: true })
      .click();
    await page
      .getByRole("textbox", {
        name: "Fecha de nacimiento (AAAA-MM-DD)",
        exact: true,
      })
      .fill("2000-01-01");
    await page.getByRole("button", { name: "Masculino", exact: true }).click();
    await page
      .getByRole("textbox", { name: "Estatura (cm)", exact: true })
      .fill("175");
    await page
      .getByRole("textbox", { name: "Peso actual (kg)", exact: true })
      .fill("75");
    await page.getByRole("button", { name: "Continuar", exact: true }).click();
    await page.getByRole("button", { name: "Continuar", exact: true }).click();
    await page
      .getByRole("button", { name: "Crear mi perfil", exact: true })
      .click();
    await page.getByText("Hola, Atleta ✦", { exact: true }).waitFor();
    console.log("Real register + login + profile work");
    await page.getByRole("tab", { name: "Entreno" }).click();
    await page
      .getByRole("button", { name: "Generar mi plan inicial", exact: true })
      .click();
    await page.getByText("Semana del plan", { exact: true }).waitFor();
    await page
      .getByRole("button", { name: /^Strength – session 1 Fase:/ })
      .click();
    await page.getByRole("checkbox").first().waitFor();
    const checkboxCount = await page.getByRole("checkbox").count();
    for (let i = 0; i < checkboxCount; i++)
      await page.getByRole("checkbox").nth(i).click();
    await page
      .getByRole("button", { name: "Completar y guardar sesión", exact: true })
      .click();
    await page.getByText("Sesión registrada", { exact: true }).waitFor();
    await page
      .getByRole("button", { name: "Ver mi registro", exact: true })
      .click();
    await page
      .getByRole("button", {
        name: "Revisar sugerencias de progresión",
        exact: true,
      })
      .click();
    await page.getByText("Para tu próxima sesión", { exact: true }).waitFor();
    console.log("Real generation + workout + history + progression work");
    // Use a fresh page to exercise re-login and domain data loaded from the API.
    await page.goto(webUrl);
    await page
      .getByRole("textbox", { name: "Correo electrónico", exact: true })
      .fill(email);
    await page
      .getByRole("textbox", { name: "Contraseña", exact: true })
      .fill("Integration123!");
    await page
      .getByRole("button", { name: "Iniciar sesión", exact: true })
      .click();
    await page.getByText("Hola, Atleta ✦", { exact: true }).waitFor();
    await page.getByRole("tab", { name: "Nutrición" }).click();
    await page
      .getByRole("button", { name: "Registrar comida", exact: true })
      .click();
    await page.getByText("Banana, raw", { exact: true }).click();
    await page
      .getByRole("textbox", { name: "Cantidad (g)", exact: true })
      .fill("100");
    await page
      .getByRole("button", { name: "Guardar comida", exact: true })
      .click();
    await page.getByText("Banana, raw", { exact: true }).waitFor();
    await page
      .getByRole("button", {
        name: "Configurar calorías y macros",
        exact: true,
      })
      .click();
    await page
      .getByRole("textbox", { name: "Calorías (kcal)", exact: true })
      .fill("2000");
    await page
      .getByRole("textbox", { name: "Proteína (g)", exact: true })
      .fill("125");
    await page
      .getByRole("textbox", { name: "Carbohidratos (g)", exact: true })
      .fill("225");
    await page
      .getByRole("textbox", { name: "Grasas (g)", exact: true })
      .fill("66.7");
    await page
      .getByRole("button", { name: "Guardar metas", exact: true })
      .click();
    await page.getByText("Dale energía a tu día", { exact: true }).waitFor();
    await page.getByRole("tab", { name: "Progreso" }).click();
    await page
      .getByRole("textbox", { name: "Peso de hoy (kg)", exact: true })
      .fill("74.5");
    await page
      .getByRole("button", { name: "Guardar peso", exact: true })
      .click();
    await page
      .getByText(
        "Peso registrado. Las metas nutricionales y el perfil no se cambian automáticamente.",
        { exact: true },
      )
      .waitFor();
    console.log("Real meals + macros + weight work");
    await page.getByRole("tab", { name: "Entreno" }).click();
    await page.getByText("Crear", { exact: true }).click();
    await page
      .getByRole("textbox", { name: "Nombre de la sesión", exact: true })
      .fill("Sesión propia E2E");
    await page
      .getByRole("button", { name: /^Bodyweight squat Fuerza/ })
      .click();
    await page
      .getByRole("button", { name: "Guardar sesión propia", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Editar mi sesión", exact: true })
      .click();
    await page
      .getByRole("textbox", { name: "Nombre de la sesión", exact: true })
      .fill("Sesión editada E2E");
    await page
      .getByRole("button", { name: "Guardar cambios de sesión", exact: true })
      .click();
    await page
      .getByText("Sesión editada E2E", { exact: true })
      .last()
      .waitFor();
    console.log("Real custom workout creation + editing work");

    if (errors.length) throw new Error("Browser errors: " + errors.join("; "));
    const api = await fetch(apiUrl + "/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password: "Integration123!" }),
    }).then((r) => r.json());
    const headers = { Authorization: "Bearer " + api.access_token };
    const summary = await fetch(apiUrl + "/progress/summary", { headers }).then(
      (r) => r.json(),
    );
    if (summary.workouts_completed !== 1 || summary.latest_weight_kg !== 74.5)
      throw new Error("API data did not match UI actions");
    console.log(
      "PASS: 5 demo screens and all core live API flows; no page errors.",
    );
    console.log(JSON.stringify({ checkboxCount, summary, errors }));
  } finally {
    if (browser) await browser.close();
    backend?.kill();
    web?.kill();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});

const required = ["NEXT_PUBLIC_API_BASE_URL", "NEXT_PUBLIC_APP_NAME"];
const forbidden = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"];

const errors = [];
for (const name of required) {
  if (!process.env[name]) {
    errors.push(`${name} is required.`);
  }
}
for (const name of forbidden) {
  if (process.env[name]) {
    errors.push(`${name} must not be exposed to the frontend environment.`);
  }
}

if (errors.length) {
  console.error("[FAIL] Frontend environment validation failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log("[OK] Frontend environment validation passed.");

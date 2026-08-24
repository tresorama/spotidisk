import { defineConfig } from 'kubb/config';
import { adapterOas } from '@kubb/adapter-oas';
import { pluginTs } from '@kubb/plugin-ts';
import { pluginZod } from '@kubb/plugin-zod';
import { pluginAxios } from '@kubb/plugin-axios';


const INPUT_URL = "http://localhost:8000/openapi.json";
const OUTPUT_DIR = {
  FNS: './src/lib/api-client/client-kubb-fns/lib/generated',
  SDK: './src/lib/api-client/client-kubb-sdk/lib/generated',
};

type SingleConfig = Parameters<typeof defineConfig>[0];

const CONFIG_FNS: SingleConfig = {
  name: "KUBB-FNS",
  root: '.',
  input: INPUT_URL,
  output: { path: OUTPUT_DIR.FNS, clean: true },
  adapter: adapterOas({
    validate: true,
    // dateType: 'date', 
    // integerType: 'number',
  }),
  plugins: [
    pluginTs({
      output: { path: './output-ts', mode: 'directory', barrel: { type: 'all' } },
      group: { type: 'tag' },
      // exclude: [{ type: 'tag', pattern: 'store' }],
      // enum: { type: 'asConst' },
      // optionalType: 'questionTokenAndUndefined',
      // resolver: {
      //   name: (name) => `Type_${formatName(name)}`,
      // }
    }),
    pluginZod({
      output: { path: './output-zod', mode: 'directory', barrel: { type: 'all' } },
      group: { type: 'tag' },
      // inferred: true,
      // importPath: 'zod',
      // resolver: {
      //   name: (name) => `schema_${formatName(name)}`,
      // }
    }),
    pluginAxios({
      output: { path: './client-axios', mode: 'directory', barrel: { type: 'named' } },
      validator: { request: 'zod', response: 'zod' },
    }),
  ],
};

const CONFIG_SDK: SingleConfig = {
  name: "KUBB-SDK",
  root: '.',
  input: INPUT_URL,
  output: { path: OUTPUT_DIR.SDK, clean: true },
  adapter: adapterOas({
    validate: true,
    // dateType: 'date', 
    // integerType: 'number',
  }),
  plugins: [
    pluginTs({
      output: { path: './output-ts', mode: 'directory', barrel: { type: 'named' } },
      group: { type: 'tag' },
      // exclude: [{ type: 'tag', pattern: 'store' }],
      // enum: { type: 'asConst' },
      // optionalType: 'questionTokenAndUndefined',
      // resolver: {
      //   name: (name) => `Type_${formatName(name)}`,
      // }
    }),
    pluginZod({
      output: { path: './output-zod', mode: 'directory', barrel: { type: 'all' } },
      group: { type: 'tag' },
      // inferred: true,
      // importPath: 'zod',
      // resolver: {
      //   name: (name) => `schema_${formatName(name)}`,
      // }
    }),
    pluginAxios({
      output: { path: './client-axios', mode: 'directory' },
      sdk: { name: "ApiClientAxios", mode: "flat" },
      validator: { request: 'zod', response: 'zod' },
    }),
  ],
};

export default defineConfig([
  CONFIG_FNS,
  CONFIG_SDK,
]);


// 

// function formatName(x: string) {
//   // input: settings_updateSettings Status 200
//   // output: Settings_UpdateSettings_Status_200
//   const capitalize = (x: string) => x.slice(0, 1).toUpperCase() + x.slice(1);
//   const joined = x
//     .replaceAll("_", " ")
//     .replaceAll(" ", "_");
//   const capped = capitalize(joined);
//   return capped;
// };
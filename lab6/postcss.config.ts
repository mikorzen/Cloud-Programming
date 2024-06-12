import type { Config } from "postcss-load-config";
import autoprefixer from "autoprefixer";
import tailwindcss from "tailwindcss";

export default {
	plugins: [tailwindcss(), autoprefixer()],
} satisfies Config;

import type { Config } from "tailwindcss";
import daisyui from "daisyui";

export default {
	content: ["static/**/*.{html,ts}", "templates/**/*.{html,ts}"],
	theme: {
		extend: {},
	},
	plugins: [daisyui],
} satisfies Config;

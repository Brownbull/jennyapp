# Option 3: Set up a One-Time Build to Extract Static Tailwind

If you want to use Tailwind UI components fully, including custom themes, you can do this:

## 🔧 Setup

Create a minimal project with Node (just once):

```bash
npm init -y
npm install tailwindcss @tailwindcss/cli
```

Add a `tailwind.config.js` like:

```js
module.exports = {
  content: ["./templates/**/*.html"], // point to your Jinja files
  theme: { extend: {} },
  plugins: [],
}
```

Create a CSS file `./jennyapp/static/src/input.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
@import "tailwindcss";
```

Run build:

```bash
npx tailwindcss -i ./jennyapp/static/src/input.css -o ./jennyapp/static/css/tailwind.css --minify
```

You now have a standalone minified CSS file with only the classes you used in your app.
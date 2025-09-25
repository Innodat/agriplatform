I'm building a web platform for agriculture businesses using React + Vite. I want to follow best practices for modular architecture and reusable components, but I'm not sure what the ideal structure looks like.

Here's what I have so far:
- The platform will eventually support multiple domains (e.g., HR, finance, logistics). For now, I only have the **receipt module**, which falls under the HR domain.
- I already have a **mobile app** built with Next.js in the `fe-mobile` folder. It captures receipts, which are then displayed in the web dashboard.
- In the web app, I have a `page.tsx` file that serves as a dashboard for both **admin and user views** of receipts.

Please help me:
1. Plan a scalable UI architecture for React + Vite that supports multiple domains and modules.
2. Suggest a folder structure that encourages modularity and reusability.
3. Recommend best practices for component design, including shared components, domain-specific components, and layout strategies.
4. Consider how to integrate or align with the existing Next.js mobile app (e.g., shared types, design consistency).
5. Optionally, propose how to handle routing, state management, and theming in a way that scales well.

Feel free to ask clarifying questions if needed.

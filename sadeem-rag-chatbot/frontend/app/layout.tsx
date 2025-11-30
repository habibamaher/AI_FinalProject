import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sadeem Chatbot - Customer Support',
  description: 'RAG-powered customer support assistant',
  icons: {
    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="75" font-size="75" font-weight="bold" fill="%2307114C">S</text></svg>',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-gradient-to-br from-slate-100 to-blue-200">
        {children}
      </body>
    </html>
  );
}

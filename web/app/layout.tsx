"use client";

import { ChakraProvider, ThemeConfig, extendTheme } from "@chakra-ui/react";
import { AppProps } from "next/app";

const config: ThemeConfig = {
  useSystemColorMode: false,
  initialColorMode: "dark",
};

const customTheme = extendTheme({
  config,
  styles: {
    global: {
      body: {
        bg: "#0A081E",
      },
    },
  },
});

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ChakraProvider theme={customTheme}>{children}</ChakraProvider>
      </body>
    </html>
  );
}

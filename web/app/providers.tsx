import React from "react";
import { ThemeConfig, extendTheme } from "@chakra-ui/react";
import { CacheProvider } from "@chakra-ui/next-js";
import { ChakraProvider } from "@chakra-ui/react";

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

const ClientOnly = ({ children, ...delegated }) => {
  const [hasMounted, setHasMounted] = React.useState(false);

  React.useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) return null;

  return <React.Fragment {...delegated}>{children}</React.Fragment>;
};

export default ClientOnly;

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClientOnly>
      <CacheProvider>
        <ChakraProvider theme={customTheme}>{children}</ChakraProvider>
      </CacheProvider>
    </ClientOnly>
  );
}

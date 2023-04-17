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

const LearningApp = ({ Component, pageProps }: AppProps) => {
  return (
    <ChakraProvider theme={customTheme}>
      <Component {...pageProps} />
    </ChakraProvider>
  );
};

export default LearningApp;

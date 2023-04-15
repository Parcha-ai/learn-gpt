import React, { useContext, useEffect } from "react";
import {
  Box,
  Button,
  Heading,
  Input,
  Container,
  FormLabel,
  InputGroup,
} from "@chakra-ui/react";
import Subject from "../components/Subject";

const Header = () => (
  <Heading
    mt={4}
    mb={4}
    textAlign="center"
    color="white"
    fontWeight={700}
    fontSize={18}
  >
    <a href="#">Learn</a>
  </Heading>
);

const Learn = () => {
  const [learnDescription, setLearnDescription] = React.useState("");
  const [showJSON, setShowJSON] = React.useState(false);

  const json = require("../../examples/nn_plan.json");

  return (
    <Container p={4} maxW="container.md">
      <Header />
      <FormLabel mt={12} px={[0, 10]}>
        <InputGroup
          background="linear-gradient(268.17deg, #0C0B20 6.09%, #2D2A3D 82.17%)"
          borderRadius={10}
        >
          <Input
            shadow="rgba(0, 0, 0, 0.1) 0px 0px 0px 1px, rgba(0, 0, 0, 0.2) 0px 5px 10px 0px, rgba(0, 0, 0, 0.4) 0px 15px 40px 0px"
            bg="whiteAlpha.50"
            size="lg"
            px={6}
            py={6}
            borderRadius={10}
            required
            color="white"
            placeholder="What do you want to learn?"
            value={learnDescription}
            style={{
              border: "1px solid #75758B",
              boxShadow: "0px 4px 20px #33313A",
              borderRadius: "10px",
            }}
            _focus={{
              background: "#2E2A3D",
            }}
            _hover={{
              background: "#2E2A3D",
            }}
            onChange={(e) => setLearnDescription(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                setShowJSON(true);
                (e.target as any).blur();
              }
            }}
          />
        </InputGroup>
      </FormLabel>
      <Box
        background="linear-gradient(268.17deg, #0C0B20 6.09%, #2D2A3D 82.17%)"
        borderRadius={10}
        hidden={showJSON}
        p={4}
        w="full"
        maxW="container.xl"
        mx="auto"
        style={{
          boxShadow: "0px 4px 20px #33313A",
          borderRadius: "10px",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          overflowX: "auto",
        }}
      >
        <Subject data={json.subject} />
      </Box>

      <Box display="flex" justifyContent="center" mt={12}>
        <Button
          colorScheme="purple"
          color="white"
          hidden={showJSON}
          borderRadius={8}
          bg="#6C70C2"
          size="xl"
          p={3.5}
          px={7}
          isDisabled={!learnDescription}
          onClick={() => setShowJSON(true)}
          fontWeight={300}
          textTransform="uppercase"
        >
          Go
        </Button>

        <Button
          colorScheme="purple"
          color="white"
          hidden={!showJSON}
          borderRadius={8}
          bg="#6C70C2"
          size="xl"
          p={3.5}
          px={7}
          isDisabled={!learnDescription}
          onClick={(e) => setShowJSON(false)}
          fontWeight={300}
          textTransform="uppercase"
        >
          Go
        </Button>
      </Box>
    </Container>
  );
};

export default Learn;

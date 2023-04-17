"use client";

import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Input,
  Container,
  FormLabel,
  InputGroup,
  Spinner,
} from "@chakra-ui/react";
import LearnHeader from "../components/LearnHeader";
import Plan from "../components/Plan";
import { createPlan } from "../api/PlanAPI";

const Learn = () => {
  const [learnDescription, setLearnDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [json, setJson] = useState(null);

  const handleCreatePlan = async () => {
    setIsLoading(true);
    try {
      const response = await createPlan({
        goal: learnDescription,
      });
      // setJson(response);
    } catch (error) {
      console.error("Error in creating plan:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container p={4} maxW="container.md">
      <LearnHeader />
      <FormLabel mt={12} px={[0, 10]}>
        <InputGroup
          background="linear-gradient(268.17deg, #0C0B20 6.09%, #2D2A3D 82.17%)"
          borderRadius={10}
        >
          <Input
            bg="whiteAlpha.50"
            borderColor="#75758B"
            borderRadius="10px"
            boxShadow="0px 4px 20px #33313A"
            color="white"
            placeholder="What do you want to learn?"
            px={6}
            py={6}
            required
            shadow="rgba(0, 0, 0, 0.1) 0px 0px 0px 1px, rgba(0, 0, 0, 0.2) 0px 5px 10px 0px, rgba(0, 0, 0, 0.4) 0px 15px 40px 0px"
            size="lg"
            value={learnDescription}
            _focus={{
              background: "#2E2A3D",
            }}
            _hover={{
              background: "#2E2A3D",
            }}
            onChange={(e) => setLearnDescription(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleCreatePlan();
                (e.target as any).blur();
              }
            }}
          />
        </InputGroup>
      </FormLabel>
      <Box display="flex" justifyContent="center" mt={12}>
        <Button
          bg="#6C70C2"
          borderRadius={8}
          color="white"
          colorScheme="purple"
          fontWeight={300}
          hidden={json !== null}
          isDisabled={!learnDescription}
          p={3.5}
          px={7}
          size="xl"
          textTransform="uppercase"
          onClick={() => handleCreatePlan()}
        >
          {isLoading ? <Spinner size="xs" color="white" /> : "Go"}
        </Button>

        <Button
          bg="#6C70C2"
          borderRadius={8}
          color="white"
          colorScheme="purple"
          fontWeight={300}
          hidden={json === null}
          p={3.5}
          px={7}
          size="xl"
          textTransform="uppercase"
          onClick={(e) => setJson(null)}
        >
          Clear
        </Button>
      </Box>
      {json && <Plan plan={json} />}
    </Container>
  );
};

export default Learn;

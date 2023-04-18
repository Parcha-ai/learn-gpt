"use client";

import React, { useState } from "react";
import {
  Box,
  Input,
  Container,
  FormLabel,
  InputGroup,
  Spinner,
  VStack,
  HStack,
  Text,
  Flex,
} from "@chakra-ui/react";
import LearnHeader from "../components/LearnHeader";
import Plan from "../components/Plan";
import TypingIndicator from "../components/TypingIndicator";
import { Plan as PlanData } from "../api/PlanAPI";
import { createPlan } from "../api/PlanAPI";

type Message = {
  type: "user" | "system";
  text: string;
};

const Learn = () => {
  const [messages, setMessages] = useState<Message[]>([
    { type: "system", text: "What do you want to learn?" },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [planData, setPlanData] = useState<PlanData | null>(null);

  const handleSystemMessage = (text: string) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: "system", text: text },
      ]);
    }, 2000);
  };

  const handleConversation = async () => {
    if (inputMessage.trim() === "") return;
    if (isLoading) return;

    setMessages([...messages, { type: "user", text: inputMessage }]);

    if (!planData) {
      try {
        setIsLoading(true);
        handleSystemMessage("Ok, let me work on that...");

        const plan = await createPlan({
          goal: inputMessage,
        });
        setPlanData(plan);

        handleSystemMessage(
          "Are you happy with the plan or do you want me to change it?"
        );
      } catch (error) {
        console.error("Error in creating plan:", error);
        handleSystemMessage(
          "Sorry, something went wrong. Please try again later."
        );
      } finally {
        setIsLoading(false);
      }
    } else {
      handleSystemMessage("Thank you for your feedback. Let me try again...");
      setIsLoading(false);
    }

    setInputMessage("");
  };

  return (
    <Container p={4} maxW="container.xl">
      <LearnHeader />
      <Flex>
        <Box
          flex={1}
          borderWidth="1px"
          borderColor="#75758B"
          borderRadius="10px"
          p={4}
        >
          <VStack
            mt={12}
            px={[0, 10]}
            spacing={4}
            width="100%"
            height="50vh"
            overflowY="auto"
          >
            {messages.map((message, index) => (
              <HStack
                key={index}
                alignSelf={message.type === "user" ? "flex-end" : "flex-start"}
                bg={message.type === "user" ? "#6C70C2" : "#A3A6CC"}
                borderRadius={8}
                color="white"
                p={3.5}
                px={5}
              >
                <Text>{message.text}</Text>
              </HStack>
            ))}

            {isTyping && (
              <HStack
                alignSelf="flex-start"
                bg="#A3A6CC"
                borderRadius={8}
                color="white"
                p={3.5}
                px={5}
              >
                <TypingIndicator />
              </HStack>
            )}
          </VStack>
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
                placeholder="Type your message here..."
                px={6}
                py={6}
                required
                shadow="rgba(0, 0, 0, 0.1) 0px 0px 0px 1px, rgba(0, 0, 0, 0.2) 0px 5px 10px 0px, rgba(0, 0, 0, 0.4) 0px 15px 40px 0px"
                size="lg"
                isDisabled={isLoading}
                value={inputMessage}
                _focus={{
                  background: "#2E2A3D",
                }}
                _hover={{
                  background: "#2E2A3D",
                }}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleConversation();
                    setInputMessage("");
                  }
                }}
              />
            </InputGroup>
          </FormLabel>
        </Box>
        <Box
          flex={1}
          borderWidth="1px"
          borderColor="#75758B"
          borderRadius="10px"
          position="relative"
          p={4}
        >
          {isLoading && (
            <Spinner
              position="absolute"
              top="50%"
              left="50%"
              transform="translate(-50%, -50%)"
              size="xl"
              color="#6C70C2"
            />
          )}
          {planData && <Plan plan={planData} />}
        </Box>
      </Flex>
    </Container>
  );
};

export default Learn;

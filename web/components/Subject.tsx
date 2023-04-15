import React from "react";
import { Box, Heading, Text, VStack } from "@chakra-ui/react";
import Resources from "./Resources";
import Exercises from "./Exercises";

const Subject = ({ data }) => {
  return (
    <VStack align="start" spacing={4}>
      <Heading color="white" size="md">
        {data.subject}
      </Heading>
      <Text color="white">{data.description}</Text>
      <Text color="white">{data.reason}</Text>
      <Resources resources={data.resources} />
      <Exercises exercises={data.exercises} />
      {data.subjects &&
        data.subjects.map((nestedSubject, index) => (
          <Box key={index} pl={4}>
            <Subject data={nestedSubject} />
          </Box>
        ))}
    </VStack>
  );
};

export default Subject;

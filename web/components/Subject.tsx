import React from "react";
import { Box, Heading, Text, VStack } from "@chakra-ui/react";
import Resources from "./Resources";
import Exercises from "./Exercises";

const Subject = ({ data }) => {
  const hasResources = data.resources && data.resources.length > 0;
  const hasExercises = data.exercises && data.exercises.length > 0;

  return (
    <VStack align="start" spacing={4}>
      <Heading color="white" size="md">
        {data.subject}
      </Heading>
      <Text color="white">{data.description}</Text>
      <Text color="white">{data.reason}</Text>
      {hasResources && (
        <Resources resources={data.resources} hasResources={hasResources} />
      )}
      {hasExercises && (
        <Exercises exercises={data.exercises} hasExercises={hasExercises} />
      )}
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

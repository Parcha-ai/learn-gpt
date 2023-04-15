import React, { useState } from "react";
import { Box, Button, Heading, Text } from "@chakra-ui/react";

const Exercises = ({ exercises }) => {
  const [showExercises, setShowExercises] = useState(false);

  return (
    <Box>
      <Button
        variant="outline"
        colorScheme="purple"
        size="sm"
        onClick={() => setShowExercises(!showExercises)}
      >
        {showExercises ? "Hide" : "Show"} Exercises
      </Button>
      {showExercises && (
        <Box mt={2} pl={4}>
          {exercises.map((exercise, index) => (
            <Box key={index} mt={2}>
              <Text color="white">{exercise.description}</Text>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default Exercises;

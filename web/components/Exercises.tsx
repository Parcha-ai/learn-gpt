"use client";

import React, { useState } from "react";
import { Button, Text, VStack } from "@chakra-ui/react";

const Exercises = ({ exercises, hasExercises }) => {
  const [showExercises, setShowExercises] = useState(false);

  if (!hasExercises || exercises.length === 0) {
    return null;
  }

  const toggleExercises = () => setShowExercises(!showExercises);

  return (
    <VStack align="start" spacing={2} pt={4}>
      <Button
        colorScheme="purple"
        variant="outline"
        size="sm"
        onClick={toggleExercises}
      >
        {showExercises ? "Hide Exercises" : "Show Exercises"}
      </Button>
      {showExercises &&
        exercises.map((exercise, index) => (
          <Text key={index} color="white">
            {exercise.description}
          </Text>
        ))}
    </VStack>
  );
};

export default Exercises;

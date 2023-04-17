"use client";

import React, { useState } from "react";
import { Button, Text, VStack } from "@chakra-ui/react";

const Resources = ({ resources, hasResources }) => {
  const [showResources, setShowResources] = useState(false);

  if (!hasResources || resources.length === 0) {
    return null;
  }

  return (
    <VStack align="start" spacing={2} pt={4}>
      <Button
        colorScheme="purple"
        variant="outline"
        size="sm"
        onClick={() => setShowResources(!showResources)}
      >
        {showResources ? "Hide Resources" : "Show Resources"}
      </Button>
      {showResources &&
        resources.map((resource, index) => (
          <VStack align="start" key={index}>
            <Text color="white" fontWeight="semibold">
              {resource.title}
            </Text>
            <Text color="white">{resource.description}</Text>
          </VStack>
        ))}
    </VStack>
  );
};

export default Resources;

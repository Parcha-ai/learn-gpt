import React, { useState } from "react";
import { Box, Button, Heading, Text } from "@chakra-ui/react";

const Resources = ({ resources }) => {
  const [showResources, setShowResources] = useState(false);

  return (
    <Box>
      <Button
        variant="outline"
        colorScheme="purple"
        size="sm"
        onClick={() => setShowResources(!showResources)}
      >
        {showResources ? "Hide" : "Show"} Resources
      </Button>
      {showResources && (
        <Box mt={2} pl={4}>
          {resources.map((resource, index) => (
            <Box key={index} mt={2}>
              <Heading size="xs" color="white">
                {resource.title}
              </Heading>
              <Text color="white">{resource.description}</Text>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default Resources;

import React from "react";
import { Box } from "@chakra-ui/react";
import Subject from "../components/Subject";

const Plan = ({ plan }) => {
  return (
    <Box
      background="linear-gradient(268.17deg, #0C0B20 6.09%, #2D2A3D 82.17%)"
      borderRadius={10}
      boxShadow="0px 4px 20px #33313A"
      maxW="container.xl"
      mx="auto"
      overflowX="auto"
      p={4}
      w="full"
      whiteSpace="pre-wrap"
      wordBreak="break-word"
    >
      <Subject data={plan.subject} />
    </Box>
  );
};

export default Plan;

import { HStack, Text } from "@chakra-ui/react";

const TypingIndicator = () => {
  return (
    <HStack alignSelf="flex-start" color="white">
      <Text>
        <span className="dot">.</span>
        <span className="dot">.</span>
        <span className="dot">.</span>
      </Text>
      <style jsx>{`
        .dot {
          animation: dot-flashing 1s infinite linear;
          opacity: 0;
        }

        .dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .dot:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes dot-flashing {
          0%,
          100% {
            opacity: 0;
          }
          50% {
            opacity: 1;
          }
        }
      `}</style>
    </HStack>
  );
};

export default TypingIndicator;

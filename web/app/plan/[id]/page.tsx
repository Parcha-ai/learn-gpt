"use client";
import { Container } from "@chakra-ui/react";

import Plan from "../../../components/Plan";
import { getPlan } from "../../../api/PlanAPI";

const PlanView = async ({ params: { id } }) => {
  const plan = await getPlan({ id: id });
  return (
    <Container p={4} maxW="container.md">
      <Plan plan={plan} />
    </Container>
  );
};

export default PlanView;

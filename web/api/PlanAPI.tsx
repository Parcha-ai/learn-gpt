import axiosClient from "./Client";

interface CreatePlanRequest {
  goal: string;
}

interface Plan {
  subject: string;
  subjects: Plan[];
  resources: string[];
  exercises: string[];
}

interface CreatePlanResponse {
  plan: Plan;
}

export const createPlan = async (
  createPlanRequest: CreatePlanRequest
): Promise<Plan> => {
  try {
    const response = await axiosClient.post<CreatePlanResponse>(
      "/v1/create_plan",
      createPlanRequest
    );
    return response.data.plan;
  } catch (error) {
    throw error;
  }
};

import axiosClient from "./Client";

interface Plan {
  goal: string;
  subject: string;
  subjects: Plan[];
  resources: string[];
  exercises: string[];
}

interface CreatePlanRequest {
  goal: string;
}

interface CreatePlanResponse {
  plan: Plan;
}

export const createPlan = async (req: CreatePlanRequest): Promise<Plan> => {
  const response = await axiosClient.post<CreatePlanResponse>(
    "/v1/create_plan",
    req
  );
  return response.data.plan;
};

interface GetPlanRequest {
  id: string;
}

interface GetPlanResponse {
  plan: Plan;
}

export const getPlan = async (req: GetPlanRequest): Promise<Plan> => {
  const response = await axiosClient.post<GetPlanResponse>("/v1/get_plan", req);
  return response.data.plan;
};

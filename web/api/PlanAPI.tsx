import axiosClient from "./Client";

export const createPlan = async (data) => {
  try {
    const response = await axiosClient.post("/v1/create_plan", data);
    return response;
  } catch (error) {
    throw error;
  }
};

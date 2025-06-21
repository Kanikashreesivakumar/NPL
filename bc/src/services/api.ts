export interface GenerateImageRequest {
  prompt: string;
  height?: number;
  width?: number;
  guidance_scale?: number;
  num_inference_steps?: number;
}

export const generateImage = async (params: GenerateImageRequest) => {
  try {
    const response = await fetch('http://localhost:8000/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error('Failed to generate image');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating image:', error);
    throw error;
  }
};
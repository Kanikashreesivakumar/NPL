interface GenerateImageResponse {
    status: string;
    image: string;
    prompt: string;
}

export const generateImage = async (prompt: string): Promise<GenerateImageResponse> => {
    try {
        const response = await fetch('http://localhost:8000/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt,
                height: 1024,
                width: 1024,
                guidance_scale: 3.5,
                num_inference_steps: 50
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to generate image');
        }

        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
};
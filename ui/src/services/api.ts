interface GenerateImageResponse {
    status: string;
    image: string;
    prompt: string;
}

interface HistoryResponse {
    id: number;
    prompt: string;
    created_at: string;
    image_path: string;
}

export const generateImage = async (prompt: string): Promise<GenerateImageResponse> => {
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

    return response.json();
};

export const getHistory = async (skip = 0, limit = 10): Promise<HistoryResponse[]> => {
    const response = await fetch(`http://localhost:8000/api/history?skip=${skip}&limit=${limit}`);
    
    if (!response.ok) {
        throw new Error('Failed to fetch history');
    }

    return response.json();
};
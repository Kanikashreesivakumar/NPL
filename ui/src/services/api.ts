interface GenerateImageResponse {
    status: string;
    image?: string;
    error?: string;
}

interface GenerateImageRequest {
    prompt: string;
    width?: number;
    height?: number;
    cfg_scale?: number;
    steps?: number;
    samples?: number;
}

export const generateImage = async (prompt: string): Promise<GenerateImageResponse> => {
    const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt,
            width: 1024,
            height: 1024,
            cfg_scale: 7.0,
            steps: 30,
            samples: 1
        } as GenerateImageRequest),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to generate image');
    }

    return response.json();
};

export const checkHealth = async () => {
    const response = await fetch('http://localhost:8000/health');
    return response.json();
};
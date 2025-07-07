interface GenerateImageResponse {
    status: string;
    image?: string;
    error?: string;
    prompt?: string;
    image_id?: string;
    filename?: string;
    expires_in_days?: number;
}

interface GenerateImageRequest {
    prompt: string;
    width?: number;
    height?: number;
}

export const generateImage = async (prompt: string): Promise<GenerateImageResponse> => {
    console.log('Sending request to backend:', prompt);
    
    const response = await fetch('http://localhost:8001/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt,
            width: 512,
            height: 512
        } as GenerateImageRequest),
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Failed to generate image');
    }

    const result = await response.json();
    console.log('Success response:', result.status);
    return result;
};

export const checkHealth = async () => {
    const response = await fetch('http://localhost:8001/health');
    return response.json();
};

export interface ImageHistory {
    id: string;
    filename: string;
    prompt: string;
    created_at: string;
    url: string;
    file_size?: number;
    width?: number;
    height?: number;
    days_ago?: number;
    expires_in_days?: number;
}

export const getImageHistory = async (): Promise<ImageHistory[]> => {
    const response = await fetch('http://localhost:8001/api/gallery');
    if (!response.ok) {
        throw new Error('Failed to fetch gallery');
    }
    const data = await response.json();
    return data.images;
};

export const deleteImage = async (imageId: string): Promise<void> => {
    const response = await fetch(`http://localhost:8001/api/gallery/${imageId}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error('Failed to delete from gallery');
    }
};

export const getGalleryStats = async () => {
    const response = await fetch('http://localhost:8001/api/stats');
    return response.json();
};

export const triggerCleanup = async () => {
    const response = await fetch('http://localhost:8001/api/cleanup', {
        method: 'POST'
    });
    return response.json();
};
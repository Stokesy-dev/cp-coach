import { Groq } from 'groq-sdk';

export async function generateRecommendationRationale(
  topic: string,
  targetRating: number,
  problemName: string,
  problemRating: number | undefined
): Promise<string> {
  try {
    const groq = new Groq({
      apiKey: process.env.GROQ_API_KEY
    });
    
    const prompt = `You are a competitive programming coach. I need a single sentence explaining why you recommended this problem.
Topic targeted: ${topic}
Target Rating for user: ${targetRating}
Problem Name: ${problemName}
Problem Rating: ${problemRating || 'unrated'}

Output ONLY the one-sentence rationale, nothing else. Address the user directly as "you". Example: "This problem is recommended because it focuses on 'Graphs' at rating 1100, which is currently your top weak area."`;

    const chatCompletion = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: 'llama-3.1-8b-instant',
      temperature: 0.5,
      max_tokens: 100,
    });

    return chatCompletion.choices[0]?.message?.content?.trim() || "This problem targets your weakness in this topic.";
  } catch (error) {
    console.error("Groq API error:", error);
    return "This problem was selected to help you practice your weakness in this topic.";
  }
}

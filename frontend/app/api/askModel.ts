export async function askModel(question: string) {
  try {
    const res = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    if (!res.ok) {
      return {
        insights: [{ text: "Server error. FastAPI might not be running." }]
      };
    }

    return await res.json();
  } catch (err) {
    console.error(err);
    return {
      insights: [{ text: "Could not reach backend." }]
    };
  }
}

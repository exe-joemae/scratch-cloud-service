import fetch from "node-fetch";

export async function getScratchProjectInfo(projectId) {
    const url = `https://api.scratch.mit.edu/projects/${projectId}`;
    const res = await fetch(url);

    if (res.status !== 200) return null;

    return await res.json();
}

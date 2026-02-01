'use client';

interface WorkflowSelectorProps {
    activeWorkflow: 'story' | 'eye_candy';
    onChange: (workflow: 'story' | 'eye_candy') => void;
}

export default function WorkflowSelector({ activeWorkflow, onChange }: WorkflowSelectorProps) {
    return (
        <div className="flex justify-center mb-6">
            <div className="bg-white p-1 rounded-xl shadow-sm border border-gray-200 inline-flex">
                <button
                    onClick={() => onChange('story')}
                    className={`
            px-6 py-2.5 rounded-lg font-semibold text-sm transition-all flex items-center gap-2
            ${activeWorkflow === 'story'
                            ? 'bg-purple-600 text-white shadow-md'
                            : 'text-gray-600 hover:bg-gray-50'
                        }
          `}
                >
                    <span>🔥</span>
                    <span>Viral Story Pipeline</span>
                </button>
                <button
                    onClick={() => onChange('eye_candy')}
                    className={`
            px-6 py-2.5 rounded-lg font-semibold text-sm transition-all flex items-center gap-2
            ${activeWorkflow === 'eye_candy'
                            ? 'bg-pink-500 text-white shadow-md'
                            : 'text-gray-600 hover:bg-gray-50'
                        }
          `}
                >
                    <span>🍬</span>
                    <span>Eye Candy Pipeline</span>
                </button>
            </div>
        </div>
    );
}

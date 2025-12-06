import { modules } from '@/data/modules';
import { ModuleType } from '@/types/codecraft';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';

interface ModuleSelectorProps {
  selectedModule: ModuleType | null;
  onSelectModule: (module: ModuleType) => void;
}

export function ModuleSelector({ selectedModule, onSelectModule }: ModuleSelectorProps) {
  return (
    <div className="p-4 border-b border-border">
      <h3 className="text-sm font-medium text-muted-foreground mb-3">Select Module</h3>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
        {modules.map((module) => (
          <button
            key={module.id}
            onClick={() => onSelectModule(module.id)}
            className={cn(
              "module-card text-left",
              selectedModule === module.id && "selected"
            )}
          >
            <div className="flex items-start gap-2">
              <span className="text-lg">{module.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <p className="text-sm font-medium truncate">{module.name}</p>
                  {selectedModule === module.id && (
                    <Check className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                  )}
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                  {module.description}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

import { Settings, User, Code2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

interface HeaderProps {
  onOpenSettings: () => void;
  userName?: string;
}

export function Header({ onOpenSettings, userName = 'User' }: HeaderProps) {
  return (
    <header className="h-16 border-b border-border bg-card/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="h-full px-4 lg:px-6 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-[hsl(199_89%_48%)] flex items-center justify-center shadow-lg">
            <Code2 className="w-5 h-5 text-primary-foreground" />
          </div>
          <div className="hidden sm:block">
            <h1 className="text-xl font-bold gradient-text">CodeCraft</h1>
            <p className="text-xs text-muted-foreground -mt-0.5">AI-Powered Full Stack Builder</p>
          </div>
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-2">
          <Button 
            variant="icon" 
            size="icon" 
            onClick={onOpenSettings}
            className="rounded-xl"
          >
            <Settings className="w-5 h-5" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-xl p-0">
                <Avatar className="h-9 w-9">
                  <AvatarImage src="" alt={userName} />
                  <AvatarFallback className="bg-gradient-to-br from-primary to-[hsl(199_89%_48%)] text-primary-foreground font-medium">
                    {userName.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{userName}</p>
                  <p className="text-xs text-muted-foreground">user@codecraft.ai</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onOpenSettings}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}

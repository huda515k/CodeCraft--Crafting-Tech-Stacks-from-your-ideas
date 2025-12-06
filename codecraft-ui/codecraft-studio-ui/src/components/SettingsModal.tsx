import { useState } from 'react';
import { X, Moon, Sun, User, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useTheme } from '@/contexts/ThemeContext';
import { UserProfile } from '@/types/codecraft';
import { useToast } from '@/hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  profile: UserProfile;
  onUpdateProfile: (profile: UserProfile) => void;
}

export function SettingsModal({ isOpen, onClose, profile, onUpdateProfile }: SettingsModalProps) {
  const { theme, toggleTheme, setTheme } = useTheme();
  const { toast } = useToast();
  const [editedProfile, setEditedProfile] = useState(profile);

  const handleSaveProfile = () => {
    onUpdateProfile(editedProfile);
    toast({
      title: "Profile updated",
      description: "Your changes have been saved successfully.",
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px] bg-card border-border">
        <DialogHeader>
          <DialogTitle className="text-xl">Settings</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="appearance" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="appearance" className="gap-2">
              <Sun className="w-4 h-4" />
              Appearance
            </TabsTrigger>
            <TabsTrigger value="profile" className="gap-2">
              <User className="w-4 h-4" />
              Profile
            </TabsTrigger>
          </TabsList>

          <TabsContent value="appearance" className="space-y-6">
            <div className="flex items-center justify-between p-4 rounded-xl bg-secondary/50">
              <div className="flex items-center gap-3">
                {theme === 'dark' ? (
                  <Moon className="w-5 h-5 text-primary" />
                ) : (
                  <Sun className="w-5 h-5 text-primary" />
                )}
                <div>
                  <p className="font-medium">Dark Mode</p>
                  <p className="text-sm text-muted-foreground">
                    Switch between light and dark themes
                  </p>
                </div>
              </div>
              <Switch
                checked={theme === 'dark'}
                onCheckedChange={toggleTheme}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setTheme('light')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  theme === 'light' 
                    ? 'border-primary bg-primary/10' 
                    : 'border-border hover:border-muted-foreground'
                }`}
              >
                <div className="w-full h-20 rounded-lg bg-[#ffffff] border border-gray-200 mb-2 flex items-center justify-center">
                  <Sun className="w-6 h-6 text-gray-600" />
                </div>
                <p className="text-sm font-medium">Light</p>
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  theme === 'dark' 
                    ? 'border-primary bg-primary/10' 
                    : 'border-border hover:border-muted-foreground'
                }`}
              >
                <div className="w-full h-20 rounded-lg bg-[#0f172a] border border-gray-700 mb-2 flex items-center justify-center">
                  <Moon className="w-6 h-6 text-gray-400" />
                </div>
                <p className="text-sm font-medium">Dark</p>
              </button>
            </div>
          </TabsContent>

          <TabsContent value="profile" className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Display Name</Label>
                <Input
                  id="name"
                  value={editedProfile.name}
                  onChange={(e) => setEditedProfile({ ...editedProfile, name: e.target.value })}
                  placeholder="Your name"
                  className="bg-secondary/50 border-0"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={editedProfile.email}
                  onChange={(e) => setEditedProfile({ ...editedProfile, email: e.target.value })}
                  placeholder="your@email.com"
                  className="bg-secondary/50 border-0"
                />
              </div>

              <Button onClick={handleSaveProfile} className="w-full gap-2" variant="gradient">
                <Save className="w-4 h-4" />
                Save Changes
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

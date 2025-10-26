import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import Icon from '@/components/ui/icon';
import { authService } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';

const PROFILE_API = 'https://functions.poehali.dev/52f7c095-46c6-423b-a7f1-107fcec4ad8d';

interface ProfileData {
  user: {
    id: number;
    username: string;
    fullName: string;
    avatar: string | null;
    bio: string | null;
    role: string;
    createdAt: string;
  };
  stats: {
    storiesCount: number;
    commentsCount: number;
  };
  recentStories: Array<{
    id: number;
    title: string;
    rating: number;
    views: number;
    likes: number;
    publishedAt: string;
  }>;
}

const Profile = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      const user = await authService.getCurrentUser();
      setCurrentUser(user);

      if (!user && !username) {
        navigate('/login');
        return;
      }

      const token = authService.getToken();
      if (!token) {
        navigate('/login');
        return;
      }

      const url = username ? `${PROFILE_API}?resource=profile&username=${username}` : `${PROFILE_API}?resource=profile`;

      const response = await fetch(url, {
        headers: {
          'X-Session-Token': token
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else {
        toast({ title: 'Ошибка загрузки профиля', variant: 'destructive' });
      }

      setLoading(false);
    };

    loadProfile();
  }, [username, navigate, toast]);

  const handleLogout = async () => {
    await authService.logout();
    navigate('/');
  };

  if (loading || !profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-horror-black via-horror-burgundy to-horror-black flex items-center justify-center">
        <div className="text-white text-xl">Загрузка...</div>
      </div>
    );
  }

  const isOwnProfile = currentUser && currentUser.id === profile.user.id;

  return (
    <div className="min-h-screen bg-gradient-to-br from-horror-black via-horror-burgundy to-horror-black">
      <header className="border-b border-horror-red/20 bg-horror-black/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={() => navigate('/')} className="text-white hover:text-horror-red">
              <Icon name="ArrowLeft" className="mr-2" size={20} />
              Назад
            </Button>
            {isOwnProfile && (
              <Button variant="ghost" onClick={handleLogout} className="text-horror-red hover:bg-horror-red/10">
                <Icon name="LogOut" className="mr-2" size={18} />
                Выйти
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="story-card border-horror-red/20 mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={profile.user.avatar || undefined} alt={profile.user.fullName} />
                  <AvatarFallback className="bg-horror-red text-white text-3xl">
                    {profile.user.fullName[0]}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-white font-heading text-2xl mb-1">
                    {profile.user.fullName}
                  </CardTitle>
                  <p className="text-horror-gray">@{profile.user.username}</p>
                  <Badge className="mt-2 bg-horror-red/20 text-horror-red border-horror-red/30">
                    {profile.user.role === 'admin' ? 'Админ' : profile.user.role === 'author' ? 'Автор' : 'Читатель'}
                  </Badge>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {profile.user.bio && (
              <p className="text-horror-gray mb-4">{profile.user.bio}</p>
            )}

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-horror-black/30 rounded-lg p-4 border border-horror-red/10">
                <div className="text-horror-gray text-sm mb-1">Рассказов</div>
                <div className="text-white text-2xl font-bold">{profile.stats.storiesCount}</div>
              </div>
              <div className="bg-horror-black/30 rounded-lg p-4 border border-horror-red/10">
                <div className="text-horror-gray text-sm mb-1">Комментариев</div>
                <div className="text-white text-2xl font-bold">{profile.stats.commentsCount}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {profile.recentStories.length > 0 && (
          <Card className="story-card border-horror-red/20">
            <CardHeader>
              <CardTitle className="text-white font-heading flex items-center">
                <Icon name="BookOpen" className="mr-2 text-horror-red" size={20} />
                Последние рассказы
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {profile.recentStories.map((story) => (
                  <div
                    key={story.id}
                    onClick={() => navigate(`/story/${story.id}`)}
                    className="bg-horror-black/30 rounded-lg p-4 border border-horror-red/10 hover:border-horror-red/30 cursor-pointer transition-all"
                  >
                    <h4 className="text-white font-semibold mb-2">{story.title}</h4>
                    <div className="flex items-center space-x-4 text-sm text-horror-gray">
                      <div className="flex items-center">
                        <Icon name="Eye" className="h-4 w-4 mr-1" />
                        {story.views}
                      </div>
                      <div className="flex items-center">
                        <Icon name="Heart" className="h-4 w-4 mr-1" />
                        {story.likes}
                      </div>
                      <div className="flex items-center">
                        <Icon name="Star" className="h-4 w-4 mr-1 text-yellow-500" />
                        {story.rating.toFixed(1)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Profile;
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { authService } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const ADMIN_API = 'https://functions.poehali.dev/52f7c095-46c6-423b-a7f1-107fcec4ad8d';

const Admin = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [stories, setStories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAdminData = async () => {
      const user = await authService.getCurrentUser();

      if (!user || user.role !== 'admin') {
        toast({ title: 'Доступ запрещен', variant: 'destructive' });
        navigate('/');
        return;
      }

      const token = authService.getToken();
      if (!token) {
        navigate('/login');
        return;
      }

      const statsRes = await fetch(`${ADMIN_API}?resource=admin&admin_resource=stats`, {
        headers: { 'X-Session-Token': token }
      });
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data.stats);
      }

      const usersRes = await fetch(`${ADMIN_API}?resource=admin&admin_resource=users&limit=100`, {
        headers: { 'X-Session-Token': token }
      });
      if (usersRes.ok) {
        const data = await usersRes.json();
        setUsers(data.users);
      }

      const storiesRes = await fetch(`${ADMIN_API}?resource=admin&admin_resource=stories&limit=100`, {
        headers: { 'X-Session-Token': token }
      });
      if (storiesRes.ok) {
        const data = await storiesRes.json();
        setStories(data.stories);
      }

      setLoading(false);
    };

    loadAdminData();
  }, [navigate, toast]);

  const toggleUserStatus = async (userId: number, currentStatus: boolean) => {
    const token = authService.getToken();
    if (!token) return;

    const response = await fetch(`${ADMIN_API}?resource=admin`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Token': token
      },
      body: JSON.stringify({
        userId,
        isActive: !currentStatus
      })
    });

    if (response.ok) {
      setUsers(users.map(u => u.id === userId ? { ...u, isActive: !currentStatus } : u));
      toast({ title: 'Статус обновлен' });
    }
  };

  if (loading || !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-horror-black via-horror-burgundy to-horror-black flex items-center justify-center">
        <div className="text-white text-xl">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-horror-black via-horror-burgundy to-horror-black">
      <header className="border-b border-horror-red/20 bg-horror-black/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-heading text-white">
              <span className="text-horror-red">ADMIN</span> PANEL
            </h1>
            <Button variant="ghost" onClick={() => navigate('/')} className="text-white hover:text-horror-red">
              <Icon name="Home" className="mr-2" size={18} />
              На главную
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="story-card border-horror-red/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-horror-gray text-sm">Всего пользователей</p>
                  <p className="text-white text-3xl font-bold">{stats.totalUsers}</p>
                </div>
                <Icon name="Users" className="text-horror-red" size={32} />
              </div>
            </CardContent>
          </Card>

          <Card className="story-card border-horror-red/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-horror-gray text-sm">Всего рассказов</p>
                  <p className="text-white text-3xl font-bold">{stats.totalStories}</p>
                </div>
                <Icon name="BookOpen" className="text-horror-red" size={32} />
              </div>
            </CardContent>
          </Card>

          <Card className="story-card border-horror-red/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-horror-gray text-sm">Комментариев</p>
                  <p className="text-white text-3xl font-bold">{stats.totalComments}</p>
                </div>
                <Icon name="MessageCircle" className="text-horror-red" size={32} />
              </div>
            </CardContent>
          </Card>

          <Card className="story-card border-horror-red/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-horror-gray text-sm">Новых за неделю</p>
                  <p className="text-white text-3xl font-bold">{stats.newUsersWeek}</p>
                </div>
                <Icon name="UserPlus" className="text-horror-red" size={32} />
              </div>
            </CardContent>
          </Card>

          <Card className="story-card border-horror-red/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-horror-gray text-sm">Рассказов/неделю</p>
                  <p className="text-white text-3xl font-bold">{stats.newStoriesWeek}</p>
                </div>
                <Icon name="TrendingUp" className="text-horror-red" size={32} />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="users" className="w-full">
          <TabsList className="bg-horror-black/50 border border-horror-red/20">
            <TabsTrigger value="users" className="data-[state=active]:bg-horror-red">
              Пользователи
            </TabsTrigger>
            <TabsTrigger value="stories" className="data-[state=active]:bg-horror-red">
              Рассказы
            </TabsTrigger>
          </TabsList>

          <TabsContent value="users">
            <Card className="story-card border-horror-red/20">
              <CardHeader>
                <CardTitle className="text-white font-heading">Управление пользователями</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between bg-horror-black/30 rounded-lg p-4 border border-horror-red/10">
                      <div>
                        <p className="text-white font-semibold">{user.fullName}</p>
                        <p className="text-horror-gray text-sm">@{user.username} • {user.email}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge className="bg-horror-red/20 text-horror-red border-horror-red/30">
                            {user.role}
                          </Badge>
                          <Badge variant={user.isActive ? 'default' : 'destructive'}>
                            {user.isActive ? 'Активен' : 'Заблокирован'}
                          </Badge>
                        </div>
                      </div>
                      <Button
                        variant={user.isActive ? 'destructive' : 'default'}
                        size="sm"
                        onClick={() => toggleUserStatus(user.id, user.isActive)}
                      >
                        {user.isActive ? 'Заблокировать' : 'Разблокировать'}
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="stories">
            <Card className="story-card border-horror-red/20">
              <CardHeader>
                <CardTitle className="text-white font-heading">Все рассказы</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stories.map((story) => (
                    <div key={story.id} className="flex items-center justify-between bg-horror-black/30 rounded-lg p-4 border border-horror-red/10">
                      <div className="flex-1">
                        <p className="text-white font-semibold">{story.title}</p>
                        <p className="text-horror-gray text-sm">Автор: {story.author}</p>
                        <div className="flex gap-4 mt-2 text-sm text-horror-gray">
                          <span>👁️ {story.views}</span>
                          <span>❤️ {story.likes}</span>
                          <span>💬 {story.comments}</span>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/story/${story.id}`)}
                        className="text-horror-red hover:bg-horror-red/10"
                      >
                        Просмотр
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Admin;
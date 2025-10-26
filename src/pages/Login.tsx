import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/lib/auth';
import Icon from '@/components/ui/icon';

const Login = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authService.login(email, password);
      toast({ title: 'Вы успешно вошли!' });
      navigate('/');
    } catch (error: any) {
      toast({
        title: 'Ошибка входа',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-horror-black via-horror-burgundy to-horror-black flex items-center justify-center px-4">
      <Card className="story-card border-horror-red/20 w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-heading text-white mb-2">
            <span className="text-horror-red">HORROR</span> STORIES
          </CardTitle>
          <CardDescription className="text-horror-gray">
            Войдите в свой аккаунт
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-horror-black/50 border-horror-red/20 text-white placeholder:text-horror-gray"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-white">Пароль</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-horror-black/50 border-horror-red/20 text-white placeholder:text-horror-gray"
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-horror-red hover:bg-horror-red/80 horror-glow"
              disabled={loading}
            >
              {loading ? (
                <>Вход...</>
              ) : (
                <>
                  <Icon name="LogIn" className="mr-2" size={18} />
                  Войти
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-horror-gray text-sm">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-horror-red hover:underline">
                Зарегистрироваться
              </Link>
            </p>
          </div>

          <div className="mt-4 text-center">
            <Link to="/" className="text-horror-gray text-sm hover:text-white">
              ← Вернуться на главную
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;

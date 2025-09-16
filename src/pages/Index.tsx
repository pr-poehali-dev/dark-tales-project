import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import Icon from '@/components/ui/icon';

interface Story {
  id: number;
  title: string;
  author: {
    name: string;
    avatar: string;
    rating: number;
    stories: number;
  };
  description: string;
  genre: string[];
  rating: number;
  views: number;
  likes: number;
  comments: number;
  publishedAt: string;
  readingTime: number;
}

const Index = () => {
  const [stories] = useState<Story[]>([
    {
      id: 1,
      title: "Тени в подвале",
      author: {
        name: "Александр Темный",
        avatar: "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
        rating: 4.8,
        stories: 23
      },
      description: "Когда старый дом начинает скрипеть по ночам, а тени на стенах становятся длиннее, становится ясно — здесь живет что-то древнее и злобное...",
      genre: ["Мистика", "Психологический ужас"],
      rating: 4.9,
      views: 1250,
      likes: 89,
      comments: 23,
      publishedAt: "2024-01-15",
      readingTime: 8
    },
    {
      id: 2,
      title: "Последний поезд",
      author: {
        name: "Мария Кровавая",
        avatar: "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
        rating: 4.6,
        stories: 15
      },
      description: "Полночный поезд, который приходит только раз в год. Пассажиры говорят, что билет в один конец стоит всего лишь душу...",
      genre: ["Сверхъестественное", "Готика"],
      rating: 4.7,
      views: 980,
      likes: 67,
      comments: 18,
      publishedAt: "2024-01-12",
      readingTime: 12
    },
    {
      id: 3,
      title: "Зеркальная комната",
      author: {
        name: "Николай Мрачный",
        avatar: "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
        rating: 4.9,
        stories: 31
      },
      description: "В каждом зеркале живет отражение, но что делать, если отражение начинает жить своей жизнью и планирует занять твое место?",
      genre: ["Паранормальное", "Триллер"],
      rating: 4.8,
      views: 1560,
      likes: 124,
      comments: 35,
      publishedAt: "2024-01-10",
      readingTime: 15
    }
  ]);

  const [topAuthors] = useState([
    { name: "Александр Темный", rating: 4.8, stories: 23, followers: 340 },
    { name: "Мария Кровавая", rating: 4.6, stories: 15, followers: 289 },
    { name: "Николай Мрачный", rating: 4.9, stories: 31, followers: 456 },
    { name: "Елена Призрачная", rating: 4.7, stories: 19, followers: 312 },
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-horror-black via-horror-burgundy to-horror-black">
      {/* Header */}
      <header className="border-b border-horror-red/20 bg-horror-black/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-3xl font-heading text-white font-bold">
                <span className="text-horror-red">HORROR</span> STORIES
              </h1>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <Button variant="ghost" className="text-white hover:text-horror-red">
                Главная
              </Button>
              <Button variant="ghost" className="text-white hover:text-horror-red">
                Лучшие
              </Button>
              <Button variant="ghost" className="text-white hover:text-horror-red">
                Новое
              </Button>
              <Button className="bg-horror-red hover:bg-horror-red/80 horror-glow">
                Добавить рассказ
              </Button>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Hero Section */}
            <div className="relative overflow-hidden rounded-lg story-card p-8 text-center">
              <div className="absolute inset-0 opacity-10">
                <img 
                  src="/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg" 
                  alt="Horror Background"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="relative z-10">
                <h2 className="text-4xl font-heading font-bold text-white mb-4">
                  Добро пожаловать в мир <span className="text-horror-red">ужасов</span>
                </h2>
                <p className="text-horror-gray text-lg mb-6">
                  Платформа для любителей мистики, триллеров и всего сверхъестественного
                </p>
                <Button className="bg-horror-red hover:bg-horror-red/80 horror-glow text-lg px-8 py-3">
                  <Icon name="PenTool" className="mr-2" size={20} />
                  Написать рассказ
                </Button>
              </div>
            </div>

            {/* Stories Feed */}
            <div>
              <h3 className="text-2xl font-heading font-bold text-white mb-6 flex items-center">
                <Icon name="BookOpen" className="mr-3 text-horror-red" size={24} />
                Последние рассказы
              </h3>
              <div className="space-y-6">
                {stories.map((story) => (
                  <Card key={story.id} className="story-card border-horror-red/20 hover:border-horror-red/50">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <Avatar className="h-12 w-12">
                            <AvatarImage src={story.author.avatar} alt={story.author.name} />
                            <AvatarFallback className="bg-horror-red text-white">
                              {story.author.name[0]}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <CardTitle className="text-white font-heading text-xl hover:text-horror-red cursor-pointer transition-colors">
                              {story.title}
                            </CardTitle>
                            <div className="flex items-center space-x-2 text-sm text-horror-gray">
                              <span>{story.author.name}</span>
                              <span>•</span>
                              <div className="flex items-center">
                                <Icon name="Star" className="h-4 w-4 text-yellow-500 fill-current" />
                                <span className="ml-1">{story.author.rating}</span>
                              </div>
                              <span>•</span>
                              <span>{story.readingTime} мин</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {story.genre.map((tag) => (
                            <Badge key={tag} variant="secondary" className="bg-horror-red/20 text-horror-red border-horror-red/30">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-horror-gray text-base mb-4 leading-relaxed">
                        {story.description}
                      </CardDescription>
                      <div className="flex items-center justify-between">
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
                            <Icon name="MessageCircle" className="h-4 w-4 mr-1" />
                            {story.comments}
                          </div>
                          <div className="flex items-center">
                            <Icon name="Star" className="h-4 w-4 mr-1 text-yellow-500" />
                            {story.rating}
                          </div>
                        </div>
                        <Button variant="ghost" className="text-horror-red hover:text-horror-red/80 hover:bg-horror-red/10">
                          Читать →
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Top Authors */}
            <Card className="story-card border-horror-red/20">
              <CardHeader>
                <CardTitle className="text-white font-heading flex items-center">
                  <Icon name="Crown" className="mr-2 text-horror-red" size={20} />
                  Топ авторы
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {topAuthors.map((author, index) => (
                  <div key={author.name} className="flex items-center justify-between p-3 rounded-lg bg-horror-burgundy/30">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-horror-red text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      <div>
                        <p className="text-white font-medium">{author.name}</p>
                        <div className="flex items-center space-x-2 text-xs text-horror-gray">
                          <span>{author.stories} рассказов</span>
                          <span>•</span>
                          <div className="flex items-center">
                            <Icon name="Star" className="h-3 w-3 text-yellow-500 fill-current" />
                            <span className="ml-1">{author.rating}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <Button size="sm" variant="outline" className="border-horror-red/30 text-horror-red hover:bg-horror-red/10">
                      <Icon name="UserPlus" size={14} className="mr-1" />
                      {author.followers}
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Stats */}
            <Card className="story-card border-horror-red/20">
              <CardHeader>
                <CardTitle className="text-white font-heading flex items-center">
                  <Icon name="BarChart3" className="mr-2 text-horror-red" size={20} />
                  Статистика
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-horror-gray">Всего рассказов</span>
                  <span className="text-white font-bold">1,247</span>
                </div>
                <Separator className="bg-horror-red/20" />
                <div className="flex items-center justify-between">
                  <span className="text-horror-gray">Активных авторов</span>
                  <span className="text-white font-bold">89</span>
                </div>
                <Separator className="bg-horror-red/20" />
                <div className="flex items-center justify-between">
                  <span className="text-horror-gray">Читателей онлайн</span>
                  <span className="text-white font-bold">324</span>
                </div>
                <Separator className="bg-horror-red/20" />
                <div className="flex items-center justify-between">
                  <span className="text-horror-gray">Новых сегодня</span>
                  <span className="text-horror-red font-bold">15</span>
                </div>
              </CardContent>
            </Card>

            {/* Popular Genres */}
            <Card className="story-card border-horror-red/20">
              <CardHeader>
                <CardTitle className="text-white font-heading flex items-center">
                  <Icon name="Tags" className="mr-2 text-horror-red" size={20} />
                  Популярные жанры
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {['Мистика', 'Психологический ужас', 'Готика', 'Сверхъестественное', 'Триллер', 'Паранормальное', 'Зомби-апокалипсис', 'Городские легенды'].map((genre) => (
                    <Badge key={genre} variant="outline" className="border-horror-red/30 text-horror-gray hover:bg-horror-red/10 hover:text-white cursor-pointer">
                      {genre}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
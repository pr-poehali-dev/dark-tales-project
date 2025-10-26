import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

interface Author {
  id: number;
  name: string;
  avatar: string;
  rating: number;
  stories: number;
}

interface Story {
  id: number;
  title: string;
  author: Author;
  description: string;
  content?: string;
  genre: string[];
  rating: number;
  views: number;
  likes: number;
  comments: number;
  publishedAt: string;
  readingTime: number;
}

interface Comment {
  id: number;
  userId: number;
  userName: string;
  text: string;
  createdAt: string;
  likes: number;
}

const StoryDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [story, setStory] = useState<Story | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStory = async () => {
      const response = await fetch(`https://functions.poehali.dev/abb0e032-b766-470f-a2cd-43149dc1dcd0?id=${id}`);
      const data = await response.json();
      setStory(data);
      
      await fetch(`https://functions.poehali.dev/3acf387b-6b3b-4ab5-b117-a0568daa269e`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ storyId: id, action: 'view', userId: 1 })
      });
      
      setLoading(false);
    };

    const fetchComments = async () => {
      const response = await fetch(`https://functions.poehali.dev/3acf387b-6b3b-4ab5-b117-a0568daa269e?storyId=${id}`);
      const data = await response.json();
      setComments(data.comments || []);
    };

    fetchStory();
    fetchComments();
  }, [id]);

  const handleLike = async () => {
    const response = await fetch(`https://functions.poehali.dev/3acf387b-6b3b-4ab5-b117-a0568daa269e`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ storyId: id, action: 'like', userId: 1 })
    });
    const data = await response.json();
    
    if (data.success && story) {
      setStory({ ...story, likes: data.likes });
      toast({ title: 'Лайк добавлен!' });
    } else {
      toast({ title: 'Вы уже лайкнули этот рассказ', variant: 'destructive' });
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    const response = await fetch(`https://functions.poehali.dev/3acf387b-6b3b-4ab5-b117-a0568daa269e`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        storyId: id,
        action: 'comment',
        userId: 1,
        userName: 'Гость',
        comment: newComment
      })
    });
    const data = await response.json();

    if (data.success) {
      setComments([data.comment, ...comments]);
      setNewComment('');
      toast({ title: 'Комментарий добавлен!' });
    }
  };

  if (loading || !story) {
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
          <Button variant="ghost" onClick={() => navigate('/')} className="text-white hover:text-horror-red">
            <Icon name="ArrowLeft" className="mr-2" size={20} />
            Назад
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="story-card border-horror-red/20">
          <CardHeader>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={story.author.avatar} alt={story.author.name} />
                  <AvatarFallback className="bg-horror-red text-white">
                    {story.author.name[0]}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-horror-gray text-sm">{story.author.name}</p>
                  <div className="flex items-center text-xs text-horror-gray">
                    <Icon name="Star" className="h-3 w-3 text-yellow-500 fill-current mr-1" />
                    <span>{story.author.rating}</span>
                    <span className="mx-2">•</span>
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

            <CardTitle className="text-white font-heading text-3xl mb-4">
              {story.title}
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <p className="text-horror-gray text-lg leading-relaxed">
              {story.description}
            </p>

            {story.content && (
              <div className="text-horror-gray leading-relaxed whitespace-pre-wrap">
                {story.content}
              </div>
            )}

            <Separator className="bg-horror-red/20" />

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <Button
                  variant="ghost"
                  onClick={handleLike}
                  className="text-horror-gray hover:text-horror-red flex items-center"
                >
                  <Icon name="Heart" className="h-5 w-5 mr-2" />
                  {story.likes}
                </Button>
                <div className="flex items-center text-horror-gray">
                  <Icon name="Eye" className="h-5 w-5 mr-2" />
                  {story.views}
                </div>
                <div className="flex items-center text-horror-gray">
                  <Icon name="MessageCircle" className="h-5 w-5 mr-2" />
                  {comments.length}
                </div>
              </div>
              <div className="flex items-center text-horror-gray text-sm">
                <Icon name="Calendar" className="h-4 w-4 mr-2" />
                {new Date(story.publishedAt).toLocaleDateString('ru-RU')}
              </div>
            </div>

            <Separator className="bg-horror-red/20" />

            <div className="space-y-4">
              <h3 className="text-xl font-heading text-white flex items-center">
                <Icon name="MessageCircle" className="mr-2 text-horror-red" size={20} />
                Комментарии ({comments.length})
              </h3>

              <div className="flex gap-3">
                <Textarea
                  placeholder="Оставьте свой комментарий..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="bg-horror-black/50 border-horror-red/20 text-white placeholder:text-horror-gray"
                />
                <Button
                  onClick={handleAddComment}
                  className="bg-horror-red hover:bg-horror-red/80 horror-glow"
                >
                  <Icon name="Send" size={18} />
                </Button>
              </div>

              <div className="space-y-3">
                {comments.map((comment) => (
                  <div key={comment.id} className="bg-horror-black/30 rounded-lg p-4 border border-horror-red/10">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-white font-semibold">{comment.userName}</p>
                        <p className="text-horror-gray text-xs">
                          {new Date(comment.createdAt).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                    </div>
                    <p className="text-horror-gray">{comment.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StoryDetail;

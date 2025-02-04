using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using MySql.Data.MySqlClient;
using System.Threading.Tasks;
using System.IO;

namespace BingBride
{
    public partial class Form1 : Form
    {
        // 定義常數
        private const int DEFAULT_SPEED = 6;
        private const int TIMER_INTERVAL = 20;
        private const int PICTURE_TIMER_INTERVAL = 5000;
        private const string CONNECTION_STRING = "server={sql_server_ip}; port=3306; user=bnb_c; password=12345678; database=bnb_wedding";
        
        private readonly int speed = DEFAULT_SPEED;
        private readonly List<string> blessingContents = new List<string>();
        private readonly List<string> imageLinks = new List<string>();
        private readonly List<string> localImages = new List<string>();
        private readonly Random random = new Random();
        
        private int blessingCount = 0;
        private int imageCount = 0;
        private int currentImageIndex = 0;
        private int currentMusicNumber = 0;
        private int playStatus = 0;
        private string basePath;

        PictureBox picture_box = new PictureBox();
        int imgur_count = 0;
        List<string> link = new List<string>();
        int r = 0;
        String path = "";
        AxWMPLib.AxWindowsMediaPlayer music_player;
        AxWMPLib.AxWindowsMediaPlayer media_player;
        int rnum = 0;

        /**
         * Initialization and create picture_box, media_player and music_player.
         *
         * picture_box for show the picture from the LINE Bot.
         * media_player for playing wedding mv.
         * music_player for playing backgrond music.
         */
        public Form1()
        {
            // initialization
            InitializeComponent();
            this.DoubleBuffered = true;

            basePath = System.IO.Directory.GetCurrentDirectory();
            InitializeImages();
            InitializeMediaControls();
            this.ShowInTaskbar = false;
        }

        private void InitializeImages()
        {
            localImages.Add(Path.Combine(basePath, @"bnb\2jXNJAo.jpg"));
            localImages.Add(Path.Combine(basePath, @"bnb\zVgqz9n.jpg"));
        }

        private void InitializeMediaControls()
        {
            InitializePictureBox();
            InitializeMediaPlayer();
            InitializeMusicPlayer();
        }

        private void InitializePictureBox()
        {
            picture_box = new PictureBox
            {
                Location = new Point(0, label1.Height + 10),
                Size = new Size(Screen.PrimaryScreen.Bounds.Width, 
                              Screen.PrimaryScreen.Bounds.Height - (label1.Height + 50)),
                SizeMode = PictureBoxSizeMode.Zoom
            };
            Controls.Add(picture_box);
        }

        /**
         * Run the timer and backgroud music.
         */
        private void Form1_Load(object sender, EventArgs e)
        {
            timer2.Interval = 20;
            timer2.Start();

            rnum = random.Next(1, 4);
            Console.WriteLine(rnum);
            music_player.URL = Path.Combine(basePath, @"music\" + rnum.ToString() + @".mp3");
            music_player.settings.volume = 100;

            timer1.Interval = 5000;
            timer1.Start();
        }

        /**
         * Get pictures link from database and show it.
         */
        private void timer1_Tick(object sender, EventArgs e)
        {
            if (imgur_count != 0)
            {
                picture_box.LoadAsync(link[imgur_count - 1]);
                imgur_count--;
            }
            else
            {
                try
                {
                    if (r != 0)
                    {
                        r = 0;
                    }
                    else
                    {
                        r = 1;
                    }
                    picture_box.LoadAsync(localImages[r]);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }

                link.Clear();

                LoadImagesFromDatabase().Wait();
            }
        }

        /**
         * Get blessings content from database and use marquee way to show it.
         */
        private void timer2_Tick(object sender, EventArgs e)
        {
            if (playStatus == 1)
            {
                music_player.Ctlcontrols.play();
                playStatus = 0;
            }

            if (label1.Left < 0 && (Math.Abs(label1.Left) > label1.Width))
            {
                label1.Left = this.Width;
                if (blessingCount <= blessingContents.Count && blessingCount != 0)
                {
                    label1.Text = blessingContents[blessingCount - 1];
                    blessingCount--;
                }
                else
                {
                    try
                    {
                        label1.Text = blessingContents[random.Next(0, blessingContents.Count)];
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    
                    blessingContents.Clear();

                    LoadBlessingsFromDatabase().Wait();
                }
                
                label1.ForeColor = Color.Red;
            }

            label1.Left -= speed;
        }

        /**
         * The hot key for Form to play the media_player/music_player.
         */
        private void Form1_KeyDown(object sender, KeyEventArgs e)
        {
            switch (e.KeyCode)
            {
                case Keys.F1:
                    this.Close();
                    break;

                case Keys.F2:
                    if (this.TopMost == false)
                    {
                        this.FormBorderStyle = FormBorderStyle.FixedSingle;
                        this.WindowState = FormWindowState.Normal;
                        this.TopMost = true;
                    }
                    else
                    {
                        this.FormBorderStyle = FormBorderStyle.None;
                        this.WindowState = FormWindowState.Maximized;
                        this.TopMost = false;
                    }
                    break;

                case Keys.F3:
                    picture_box.Visible = true;
                    try
                    {
                        media_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    media_player.Visible = false;
                    music_player.URL = Path.Combine(basePath, @"music\" + random.Next(1, 4).ToString() + @".mp3");
                    music_player.Ctlcontrols.play();
                    break;

                case Keys.F4:
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = Path.Combine(basePath, @"bnb\WEDDING.wmv");
                    break;

                case Keys.F5:
                    music_player.Ctlcontrols.stop();
                    music_player.URL = Path.Combine(basePath, @"music\Wherever_You_Go.mp3");
                    playStatus = 1;
                    break;

                case Keys.F12:
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = Path.Combine(basePath, @"bnb\blessing.wmv");
                    break;
            }
            
        }

        /**
         * The hot key for MediaPlayer to play the media_player/music_player.
         */
        private void axWindowsMediaPlayer_KeyDownEvent(object sender, AxWMPLib._WMPOCXEvents_KeyDownEvent e)
        {
            switch (e.nKeyCode)
            {
                case 112: // F1
                    this.Close();
                    break;

                case 113: // F2
                    if (this.TopMost == false)
                    {
                        this.FormBorderStyle = FormBorderStyle.FixedSingle;
                        this.WindowState = FormWindowState.Normal;
                        this.TopMost = true;
                    }
                    else
                    {
                        this.FormBorderStyle = FormBorderStyle.None;
                        this.WindowState = FormWindowState.Maximized;
                        this.TopMost = false;
                    }
                    break;

                case 114: // F3
                    picture_box.Visible = true;
                    try
                    {
                        media_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    media_player.Visible = false;
                    music_player.URL = Path.Combine(basePath, @"music\" + random.Next(1, 4).ToString() + @".mp3");
                    music_player.Ctlcontrols.play();
                    break;

                case 115: // F4
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = Path.Combine(basePath, @"bnb\WEDDING.wmv");
                    break;

                case 116: // F5
                    music_player.Ctlcontrols.stop();
                    music_player.URL = Path.Combine(basePath, @"music\Wherever_You_Go.mp3");
                    playStatus = 1;
                    break;

                case 121: // F10
                    break;

                case 123: // F12
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = Path.Combine(basePath, @"bnb\blessing.wmv");
                    break;
            }
        }

        private void axWindowsMediaPlayer_MediaChange(object sender, AxWMPLib._WMPOCXEvents_MediaChangeEvent e)
        {
            if (music_player.status == "完成")
            {
                int num = random.Next(1, 4);
                while (rnum == num)
                {
                    num = random.Next(1, 4);
                }
                rnum = num;
                music_player.Ctlcontrols.stop();
                music_player.URL = Path.Combine(basePath, @"music\" + rnum.ToString() + @".mp3");
                playStatus = 1;
            }
        }

        private async Task LoadBlessingsFromDatabase()
        {
            using (var connection = new MySqlConnection(CONNECTION_STRING))
            {
                try
                {
                    await connection.OpenAsync();
                    string query = $"SELECT * FROM wedding_blessing WHERE wedding_blessing_timestamp >= '{DateTime.Now:yyyy-MM-dd}'";
                    
                    using (var command = new MySqlCommand(query, connection))
                    using (var reader = await command.ExecuteReaderAsync())
                    {
                        blessingContents.Clear();
                        while (await reader.ReadAsync())
                        {
                            blessingContents.Add($"{reader.GetString(1)}：{reader.GetString(2)}");
                            blessingCount++;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Database error: {ex.Message}");
                    // 可以考慮添加更好的錯誤處理機制
                }
            }
        }

        private async Task LoadImagesFromDatabase()
        {
            using (var connection = new MySqlConnection(CONNECTION_STRING))
            {
                try
                {
                    await connection.OpenAsync();
                    string query = $"SELECT * FROM wedding_image WHERE wedding_image_timestamp >= '{DateTime.Now:yyyy-MM-dd}'";
                    
                    using (var command = new MySqlCommand(query, connection))
                    using (var reader = await command.ExecuteReaderAsync())
                    {
                        imageLinks.Clear();
                        while (await reader.ReadAsync())
                        {
                            imageLinks.Add(reader.GetString(1));
                            imageCount++;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Database error: {ex.Message}");
                }
            }
        }
    }
}

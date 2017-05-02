/**
 * Created by jihongfei on 4/28/17.
 */

//import Datepicker from 'vuejs-datepicker';
Vue.use(VueRouter);

Date.prototype.yyyymmdd = function() {
  var mm = this.getMonth() + 1; // getMonth() is zero-based
  var dd = this.getDate();

  return [this.getFullYear(),
          (mm>9 ? '' : '0') + mm,
          (dd>9 ? '' : '0') + dd
         ].join('');
};


var yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);



var data = {
    publishers: ['人教版'],
    semesters: [],
    chapters: [],
    chosenPublisher: "教材版本",
    chosenSemester: "年级",
    chosenChapter: "章节",
    chosenTopicId: "",
    videoData: null,
    practiceData: null,
    topicData: null,
    columns: ['name','enterTopic.pv'],
    startDate: "20170109",
    endDate: yesterday.yyyymmdd()
  };


const Foo = { template: '<div>hello, {{$route.params.topicId}}</div>' };
const Bar = { template: '<div>bar</div>' };

const VideoDetail = {
  template: "#videoDetail",
  data: function() {
    this.$http.get('/api/videoStats/' + data.chosenTopicId + '/' + data.startDate + '/' + data.endDate).then(function(res){
      data.videoData = res.data;
    });
    return data;
  },
  methods: {
    returnX: function(){
      router.push({path: '/'});
      //console.log('hey')
    }
  }
};

const PracticeDetail = {
  template: "#practiceDetail",
  data: function() {
    this.$http.get('/api/practiceStats/' + data.chosenTopicId + '/' + data.startDate + '/' + data.endDate).then(function(res){
      data.practiceData = res.data;
    });
    return data;
  },
  methods: {
    returnX: function(){
      router.push({path: '/'});
      //console.log('hey')
    }
  }
};

const Default = {
  template: '#default',
  data: function () {
    this.$http.get('/api/publishers').then(function(res){
      data.publishers = res.data;
    });
    return data;

  },
  methods: {
    choosePublisher: function(publisher){
      this.chosenPublisher = publisher;
      this.$http.get('/api/semesters/' + publisher).then(function(res){
        this.semesters = res.data;
      });
    },
    chooseSemester: function(semester) {
      this.chosenSemester = semester;
      this.$http.get('/api/chapters/' + this.chosenPublisher + '/' + semester).then(function(res){
        this.chapters = res.data;
      })
    },
    chooseChapter: function(chapter) {
      this.chosenChapter = chapter.chapterName;
      this.$http.get('/api/topicStats/' + chapter.chapterId + '/' + this.startDate + '/' + this.endDate).then(function(res){
        this.topicData = res.data;
      })
    },
    clickTopic: function(pageType, topicId){
      this.chosenTopicId = topicId;
      if (pageType == "video") {
        router.push({ path: "/video/" + topicId})
      }
      else {
        router.push({ path: "/practice/" + topicId})
      }

    }
  }
};

//Vue.component('Default', {
//
//    template: '#default'
//    //props: ['name'],
//});

var routes = [
  { path: '/', component: Default},
  //{ path: '/#', component: Default},
  { path: '/video/:topicId', component: VideoDetail },
  { path: '/practice/:topicId', component: PracticeDetail },
  { path: '/bar', component: Bar }
];


var router = new VueRouter({
  routes: routes
});


var app = new Vue({
  el: '#app',
  router: router
});
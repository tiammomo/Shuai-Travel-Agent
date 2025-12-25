import { Layout } from 'antd';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import './App.css';

const { Sider, Content } = Layout;

function App() {
  return (
    <AppProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          width={300}
          style={{
            background: '#fff',
            borderRight: '1px solid #f0f0f0',
          }}
        >
          <Sidebar />
        </Sider>
        <Layout>
          <Content style={{ background: '#f5f5f5' }}>
            <ChatArea />
          </Content>
        </Layout>
      </Layout>
    </AppProvider>
  );
}

export default App;
